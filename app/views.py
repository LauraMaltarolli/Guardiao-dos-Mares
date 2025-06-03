from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from datetime import date
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from .forms import DenunciaForm, EventoForm
from django.urls import reverse_lazy

# Create your views here.
# Index
class IndexView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Buscar campanhas ativas
        hoje = date.today()
        campanhas_ativas = Campanha.objects.filter(data_inicio__lte=hoje, data_fim__gte=hoje)

        # Buscar tubarões mais ameaçados (ex: Criticamente Ameaçados e Ameaçados)
        tubaroes_ameacados = Tubarao.objects.filter(nivel_ameaca__in=['Criticamente Ameaçada', 'Ameaçada'])

        # Buscar últimas denúncias (exibir as 5 mais recentes)
        denuncias_recentes = Denuncia.objects.order_by('-data')[:5]

        # Buscar próximos eventos (data maior ou igual a hoje)
        proximos_eventos = Evento.objects.filter(data__gte=hoje).order_by('data')[:5]

        contexto = {
            'campanhas_ativas': campanhas_ativas,
            'tubaroes_ameacados': tubaroes_ameacados,
            'denuncias_recentes': denuncias_recentes,
            'proximos_eventos': proximos_eventos,
        }

        return render(request, 'index.html', contexto)

    def post(self, request):
        pass

# Login
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Buscar e armazenar a instância específica do usuário na sessão
            try:
                pesquisador = Pesquisador.objects.get(id=user.id)
                request.session['user_type'] = 'pesquisador'
            except Pesquisador.DoesNotExist:
                try:
                    organizacao = Organizacao.objects.get(id=user.id)
                    request.session['user_type'] = 'organizacao'
                except Organizacao.DoesNotExist:
                    request.session['user_type'] = 'usuario' # Ou outra identificação

            return redirect('index')
        else:
            messages.error(request, 'Usuario ou senha inválidos')
            return render(request, 'login.html')


# Logout
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    

# Cadastro
class CadastroView(View):
    def get(self, request):
        return render(request, 'cadastro.html')

    def post(self, request):
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirmar_senha = request.POST.get('password2')
        nome_cidade = request.POST.get('cidade')
        uf = request.POST.get('estado')
        tipo_usuario = request.POST.get('tipo_usuario')

        if password != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('cadastro')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
            return redirect('cadastro')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return redirect('cadastro')

        # Verificar se a cidade já existe, se não, cria
        cidade_obj, _ = Cidade.objects.get_or_create(
            nome=nome_cidade.strip().title(),
            uf=uf.strip().upper()
        )

        # Criar usuário base (sem salvar ainda)
        user = Usuario(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            cidade=cidade_obj
        )
        user.set_password(password)
        user.save()

        # Criar o tipo específico
        if tipo_usuario == 'cidadao':
            telefone = request.POST.get('telefone')
            cpf = request.POST.get('cpf')
            Cidadao.objects.create(
                id=user.id,
                telefone=telefone,
                cpf=cpf,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=user.password,
                cidade=cidade_obj,
            )
        elif tipo_usuario == 'organizacao':
            nome_fantasia = request.POST.get('nome_fantasia')
            site = request.POST.get('site')
            contato = request.POST.get('contato')
            Organizacao.objects.create(
                id=user.id,
                nome_fantasia=nome_fantasia,
                site=site,
                contato=contato,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=user.password,
                cidade=cidade_obj,
            )
        elif tipo_usuario == 'pesquisador':
            instituicao = request.POST.get('instituicao')
            area_atuacao = request.POST.get('area_atuacao')
            Pesquisador.objects.create(
                id=user.id,
                instituicao=instituicao,
                area_atuacao=area_atuacao,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=user.password,
                cidade=cidade_obj,
            )
        else:
            messages.error(request, 'Tipo de usuário inválido.')
            user.delete()
            return redirect('cadastro')

        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('index')



# Perfil
class PerfilView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        usuario = request.user

        campanhas = None

        # Dados relacionados
        denuncias = Denuncia.objects.filter(usuario=usuario)
        eventos = Evento.objects.filter(participantes=usuario)
        comentarios = Comentario.objects.filter(usuario=usuario)

        # Verificar o tipo de usuário
        tipo_usuario = "Usuário"
        dados_especificos = None

        if Cidadao.objects.filter(id=usuario.id).exists():
            tipo_usuario = "Cidadão"
            dados_especificos = Cidadao.objects.get(id=usuario.id)

        elif Organizacao.objects.filter(id=usuario.id).exists():
            tipo_usuario = "Organização"
            dados_especificos = Organizacao.objects.get(id=usuario.id)
            campanhas = Campanha.objects.filter(organizacao=dados_especificos)
        else:
            campanhas = None

        if Pesquisador.objects.filter(id=usuario.id).exists():
            tipo_usuario = "Pesquisador"
            dados_especificos = Pesquisador.objects.get(id=usuario.id)

        contexto = {
            'usuario': usuario,
            'tipo_usuario': tipo_usuario,
            'dados_especificos': dados_especificos,
            'denuncias': denuncias,
            'eventos': eventos,
            'comentarios': comentarios,
            'campanhas': campanhas,
        }

        return render(request, 'perfil.html', contexto)

    def post(self, request):
        pass

# Campanha
class CampanhaView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        campanhas = Campanha.objects.all()
        return render(request, 'campanha.html', {'campanhas': campanhas})

    def post(self, request):
        pass

# Ataques
class AtaquesView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        return render(request, 'ataque.html')

    def post(self, request):
        pass


# Evento
class EventoView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        print(f"Na EventoView - Usuário logado: {request.user.username}, Tipo: {type(request.user)}")
        pode_criar_evento = False
        if request.user.is_authenticated:
            user_type = request.session.get('user_type')
            if user_type == 'pesquisador' or user_type == 'organizacao':
                pode_criar_evento = True
                print(f"Na EventoView - Tipo de usuário da sessão: {user_type}")
            else:
                print(f"Na EventoView - Tipo de usuário da sessão: {user_type}")
        eventos = Evento.objects.all()
        create_event_form = EventoForm()
        return render(request, 'evento.html', {'eventos': eventos, 'create_event_form': create_event_form, 'pode_criar_evento': pode_criar_evento})

    def post(self, request, *args, **kwargs):
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.save() 

            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('lista_eventos')
        else:
            eventos = Evento.objects.all()
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': form.errors.as_json()})
            else:
                return render(request, 'evento.html', {'eventos': eventos, 'create_event_form': form})


class ParticiparEventoView(LoginRequiredMixin, View):
    def post(self, request, evento_id):
        print(f"ParticiparEventoView acionada para evento_id: {evento_id}, usuário: {request.user.username}")
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            evento = get_object_or_404(Evento, id=evento_id)
            print(f"Evento encontrado: {evento.titulo}")
            if request.user not in evento.participantes.all():
                print(f"Usuário {request.user.username} não está participando, adicionando...")
                evento.participantes.add(request.user)
                print(f"Participantes agora: {evento.participantes.count()}")
                return JsonResponse({'success': True, 'participantes_count': evento.participantes.count()})
            else:
                print(f"Usuário {request.user.username} já está participando.")
                return JsonResponse({'success': False, 'error': 'Você já está participando deste evento.'})
        else:
            print("Requisição inválida (não AJAX).")
            return JsonResponse({'success': False, 'error': 'Requisição inválida.'}, status=400)

class SairEventoView(LoginRequiredMixin, View):
    def post(self, request, evento_id):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            evento = get_object_or_404(Evento, id=evento_id)
            if request.user in evento.participantes.all():
                evento.participantes.remove(request.user)
                return JsonResponse({'success': True, 'participantes_count': evento.participantes.count()})
            else:
                return JsonResponse({'success': False, 'error': 'Você não está participando deste evento.'})
        return JsonResponse({'success': False, 'error': 'Requisição inválida.'}, status=400)
    
class ListarParticipantesView(LoginRequiredMixin, View):
    def get(self, request, evento_id):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            evento = get_object_or_404(Evento, id=evento_id)
            participantes = evento.participantes.values('username').all()
            participantes_list = list(participantes)
            return JsonResponse({'success': True, 'participantes': participantes_list})
        return JsonResponse({'success': False, 'error': 'Requisição inválida.'}, status=400)

listar_participantes = ListarParticipantesView.as_view()

# Tubarões
class TubaraoView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        tubaroes = Tubarao.objects.all()
        return render(request, 'tubarao.html', {'tubaroes': tubaroes})

    def post(self, request):
        pass

# Denúncia
class CriarDenunciaView(LoginRequiredMixin, View):
    login_url = 'login'
    form_class = DenunciaForm 
    success_url = reverse_lazy('lista_denuncias')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        denuncias = Denuncia.objects.all()
        return render(request, 'denuncia.html', {'form': form, 'denuncias': denuncias})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            denuncia = form.save(commit=False)
            denuncia.usuario = request.user
            denuncia.save()
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect(self.success_url)
        else:
            denuncias = Denuncia.objects.all()
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': form.errors.as_json()})
            else:
                return render(request, 'denuncia.html', {'form': form, 'denuncias': denuncias})

# Comentários
class ComentarioView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        comentarios = Comentario.objects.all()
        return render(request, 'comentario.html', {'comentarios': comentarios})

    def post(self, request):
        pass


class ComentarCampanhaView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, campanha_id):
        campanha = get_object_or_404(Campanha, id=campanha_id)
        texto = request.POST.get('texto')

        if texto:
            comentario = Comentario.objects.create(
                campanha=campanha,
                usuario=request.user,
                texto=texto,
                data=timezone.now().date() # Or timezone.now() if you want datetime
            )
            return JsonResponse({
                'success': True,
                'comentario': {
                    'texto': comentario.texto,
                    'data': comentario.data.strftime('%d/%m/%Y'),
                    'usuario': comentario.usuario.username
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'O comentário não pode estar vazio.'})
