from django.db import models
from django.contrib.auth.models import AbstractUser

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.nome} - {self.uf}"

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"


class Usuario(AbstractUser):
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


class Cidadao(Usuario):
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14, unique=True)

    class Meta:
        verbose_name = "Cidadão"
        verbose_name_plural = "Cidadãos"


class Organizacao(Usuario):
    nome_fantasia = models.CharField(max_length=100)
    site = models.URLField(blank=True, null=True)
    contato = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"


class Pesquisador(Usuario):
    instituicao = models.CharField(max_length=150)
    area_atuacao = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Pesquisador"
        verbose_name_plural = "Pesquisadores"


class Tubarao(models.Model):
    nome_comum = models.CharField(max_length=100)
    nome_cientifico = models.CharField(max_length=150)
    AMEACA_CHOICES = (
        ('Extinta', 'Extinta'),
        ('Criticamente Ameaçada', 'Criticamente Ameaçada'),
        ('Ameaçada', 'Ameaçada'),
        ('Vulnerável', 'Vulnerável'),
        ('Pouco Preocupante', 'Pouco Preocupante'),
    )
    nivel_ameaca = models.CharField(max_length=50, choices=AMEACA_CHOICES)
    descricao = models.TextField()
    curiosidade = models.TextField()
    imagem = models.ImageField(upload_to='tubaroes/')

    def __str__(self):
        return f"{self.nome_comum} ({self.nome_cientifico})"

    class Meta:
        verbose_name = "Tubarão"
        verbose_name_plural = "Tubarões"


class Campanha(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    organizacao = models.ForeignKey(Organizacao, on_delete=models.CASCADE)  # Apenas ONGs

    def __str__(self):
        return f"{self.titulo} - {self.organizacao.nome_fantasia}"

    class Meta:
        verbose_name = "Campanha"
        verbose_name_plural = "Campanhas"


class Denuncia(models.Model):
    descricao = models.TextField()
    data = models.DateField()
    local = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='denuncias/')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Denúncia {self.local}"

    class Meta:
        verbose_name = "Denúncia"
        verbose_name_plural = "Denúncias"

# ManyToMany do Django cria sozinha uma tabela intermediária para relacionar os modelos,
# então não precisamos definir uma tabela intermediária manualmente para o relacionamento entre Evento e Usuario.
class Evento(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    data = models.DateField()
    local = models.CharField(max_length=100)
    participantes = models.ManyToManyField(Usuario, blank=True)

    def __str__(self):
        return f"Evento {self.titulo} - {self.local}"

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        

class Comentario(models.Model):
    texto = models.TextField()
    data = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    campanha = models.ForeignKey(Campanha, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comentário {self.usuario.username} - {self.campanha.titulo}"

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"


class Feedback(models.Model):
    TIPOS = (
        ('Sugestão', 'Sugestão'),
        ('Crítica', 'Crítica'),
        ('Elogio', 'Elogio'),
    )
    texto = models.TextField()
    data = models.DateField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo} - {self.usuario.username}"

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
