from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from datetime import date
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

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
            return redirect('index')  # Redireciona para a página inicial
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
        feedbacks = Feedback.objects.filter(usuario=usuario)

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
            'feedbacks': feedbacks,
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
        eventos = Evento.objects.all()
        return render(request, 'evento.html', {'eventos': eventos})

    def post(self, request):
        pass


# Tubarões
class TubaraoView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        tubaroes = Tubarao.objects.all()
        return render(request, 'tubarao.html', {'tubaroes': tubaroes})

    def post(self, request):
        pass


# Denúncias
class DenunciaView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        denuncias = Denuncia.objects.all()
        return render(request, 'denuncia.html', {'denuncias': denuncias})

    def post(self, request):
        pass


# Comentários
class ComentarioView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        comentarios = Comentario.objects.all()
        return render(request, 'comentario.html', {'comentarios': comentarios})

    def post(self, request):
        pass


# Feedbacks
class FeedbackView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        feedbacks = Feedback.objects.all()
        return render(request, 'feedback.html', {'feedbacks': feedbacks})

    def post(self, request):
        pass