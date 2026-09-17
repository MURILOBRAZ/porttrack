from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("clientes", views.ClienteViewSet, basename="api-cliente")
router.register("conteineres", views.ConteinerViewSet, basename="api-conteiner")
router.register("movimentacoes", views.MovimentacaoViewSet, basename="api-movimentacao")

urlpatterns = [
    path("", include(router.urls)),
    path("relatorio/", views.RelatorioView.as_view(), name="api-relatorio"),
    path("dashboard/", views.DashboardView.as_view(), name="api-dashboard"),
]
