from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Clientes
    path("clientes/", views.ClienteListView.as_view(), name="cliente_list"),
    path("clientes/novo/", views.ClienteCreateView.as_view(), name="cliente_create"),
    path("clientes/<int:pk>/", views.ClienteDetailView.as_view(), name="cliente_detail"),
    path("clientes/<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="cliente_update"),
    path("clientes/<int:pk>/excluir/", views.ClienteDeleteView.as_view(), name="cliente_delete"),
    # Contêineres
    path("conteineres/", views.ConteinerListView.as_view(), name="conteiner_list"),
    path("conteineres/novo/", views.ConteinerCreateView.as_view(), name="conteiner_create"),
    path("conteineres/<int:pk>/", views.ConteinerDetailView.as_view(), name="conteiner_detail"),
    path("conteineres/<int:pk>/editar/", views.ConteinerUpdateView.as_view(), name="conteiner_update"),
    path("conteineres/<int:pk>/excluir/", views.ConteinerDeleteView.as_view(), name="conteiner_delete"),
    # Movimentações
    path("movimentacoes/", views.MovimentacaoListView.as_view(), name="movimentacao_list"),
    path("movimentacoes/nova/", views.MovimentacaoCreateView.as_view(), name="movimentacao_create"),
    path("movimentacoes/<int:pk>/editar/", views.MovimentacaoUpdateView.as_view(), name="movimentacao_update"),
    path("movimentacoes/<int:pk>/excluir/", views.MovimentacaoDeleteView.as_view(), name="movimentacao_delete"),
    path("movimentacoes/<int:pk>/finalizar/", views.MovimentacaoFinalizarView.as_view(), name="movimentacao_finalizar"),
    # Relatório
    path("relatorio/", views.RelatorioView.as_view(), name="relatorio"),
    path("relatorio/csv/", views.RelatorioCsvView.as_view(), name="relatorio_csv"),
]
