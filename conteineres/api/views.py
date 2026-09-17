from django.db.models import Count, ProtectedError
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import services
from ..filters import ConteinerFilter, MovimentacaoFilter
from ..models import Cliente, Conteiner, Movimentacao
from .serializers import (
    ClienteSerializer,
    ConteinerSerializer,
    MovimentacaoSerializer,
    RelatorioClienteSerializer,
)


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    search_fields = ["nome", "documento", "email"]
    ordering_fields = ["nome", "criado_em", "total_conteineres"]

    def get_queryset(self):
        return Cliente.objects.annotate(total_conteineres=Count("conteineres")).order_by("nome")

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Não é possível excluir um cliente que possui contêineres cadastrados."},
                status=status.HTTP_409_CONFLICT,
            )


class ConteinerViewSet(viewsets.ModelViewSet):
    serializer_class = ConteinerSerializer
    filterset_class = ConteinerFilter
    ordering_fields = ["numero", "criado_em"]
    queryset = Conteiner.objects.select_related("cliente")

    @extend_schema(responses=MovimentacaoSerializer(many=True))
    @action(detail=True, methods=["get"])
    def movimentacoes(self, request, pk=None):
        """Histórico de movimentações do contêiner."""
        conteiner = self.get_object()
        page = self.paginate_queryset(conteiner.movimentacoes.select_related("conteiner"))
        serializer = MovimentacaoSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class MovimentacaoViewSet(viewsets.ModelViewSet):
    serializer_class = MovimentacaoSerializer
    filterset_class = MovimentacaoFilter
    ordering_fields = ["data_inicio", "data_fim", "tipo"]
    queryset = Movimentacao.objects.select_related("conteiner")


class RelatorioView(APIView):
    @extend_schema(responses=RelatorioClienteSerializer(many=True))
    def get(self, request):
        """Movimentações por cliente e tipo, com totais de importação/exportação."""
        return Response(RelatorioClienteSerializer(services.relatorio_por_cliente(), many=True).data)


class DashboardView(APIView):
    @extend_schema(responses={200: dict})
    def get(self, request):
        """Indicadores gerais usados no dashboard."""
        return Response(
            {
                "indicadores": services.indicadores_gerais(),
                "movimentacoes_por_tipo": services.movimentacoes_por_tipo(),
                "movimentacoes_por_dia": services.movimentacoes_por_dia(30),
            }
        )
