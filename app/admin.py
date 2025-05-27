from django.contrib import admin
from .models import *

class MapaInline(admin.TabularInline):
    model = Mapa
    extra = 1

class TubaraoAdmin(admin.ModelAdmin):
    inlines = [MapaInline]

class CampanhaInline(admin.TabularInline):
    model = Campanha
    extra = 1

class OrganizacaoAdmin(admin.ModelAdmin):
    inlines = [CampanhaInline]


admin.site.register(Cidade)
admin.site.register(Usuario)
admin.site.register(Cidadao)
admin.site.register(Pesquisador)
admin.site.register(Tubarao, TubaraoAdmin)
admin.site.register(Organizacao, OrganizacaoAdmin)
admin.site.register(Campanha)
admin.site.register(Denuncia)
admin.site.register(Evento)
admin.site.register(Mapa)
admin.site.register(Comentario)
admin.site.register(Feedback)
