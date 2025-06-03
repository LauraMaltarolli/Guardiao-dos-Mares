from django.contrib import admin
from .models import *

class CampanhaInline(admin.TabularInline):
    model = Campanha
    extra = 1

class OrganizacaoAdmin(admin.ModelAdmin):
    inlines = [CampanhaInline]

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 1

class CampanhaAdmin(admin.ModelAdmin):
    inlines = [ComentarioInline]

admin.site.register(Cidade)
admin.site.register(Usuario)
admin.site.register(Cidadao)
admin.site.register(Pesquisador)
admin.site.register(Tubarao)
admin.site.register(Organizacao, OrganizacaoAdmin)
admin.site.register(Campanha, CampanhaAdmin)
admin.site.register(Denuncia)
admin.site.register(Evento)
admin.site.register(Comentario)
