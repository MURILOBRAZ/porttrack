from django.contrib import admin

from .models import Cliente, Conteiner, Movimentacao


class MovimentacaoInline(admin.TabularInline):
    model = Movimentacao
    extra = 0
    fields = ("tipo", "data_inicio", "data_fim", "observacao")


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "documento", "email", "criado_em")
    search_fields = ("nome", "documento", "email")


@admin.register(Conteiner)
class ConteinerAdmin(admin.ModelAdmin):
    list_display = ("numero", "cliente", "tipo", "status", "categoria", "criado_em")
    list_filter = ("tipo", "status", "categoria")
    search_fields = ("numero", "cliente__nome")
    list_select_related = ("cliente",)
    autocomplete_fields = ("cliente",)
    inlines = [MovimentacaoInline]


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ("conteiner", "tipo", "data_inicio", "data_fim")
    list_filter = ("tipo",)
    search_fields = ("conteiner__numero", "conteiner__cliente__nome")
    list_select_related = ("conteiner",)
    autocomplete_fields = ("conteiner",)
    date_hierarchy = "data_inicio"
