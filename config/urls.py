"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(), name='login'),
    path('index/', IndexView.as_view(), name='index'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('ataque/', AtaquesView.as_view(), name='ataque'),
    path('campanhas/', CampanhaView.as_view(), name='campanha'),
    path('eventos/', EventoView.as_view(), name='evento'),
    path('eventos/<int:evento_id>/participar/', ParticiparEventoView.as_view(), name='participar_evento'),
    path('eventos/<int:evento_id>/sair/', SairEventoView.as_view(), name='sair_evento'),
    path('eventos/<int:evento_id>/participantes/', listar_participantes, name='listar_participantes'),
    path('tubaroes/', TubaraoView.as_view(), name='tubarao'),
    path('denuncias/', CriarDenunciaView.as_view(), name='denuncia'),
    path('comentarios/', ComentarioView.as_view(), name='comentario'),
    path('campanhas/<int:campanha_id>/comentar/', ComentarCampanhaView.as_view(), name='comentar_campanha'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
