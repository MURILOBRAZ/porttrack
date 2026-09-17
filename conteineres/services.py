"""Consultas agregadas usadas pelo dashboard, relatório e API."""

from collections import OrderedDict
from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Cliente, Conteiner, Movimentacao


def indicadores_gerais() -> dict:
    conteineres = Conteiner.objects.aggregate(
        total=Count("id"),
        cheios=Count("id", filter=Q(status=Conteiner.Status.CHEIO)),
        vazios=Count("id", filter=Q(status=Conteiner.Status.VAZIO)),
        importacao=Count("id", filter=Q(categoria=Conteiner.Categoria.IMPORTACAO)),
        exportacao=Count("id", filter=Q(categoria=Conteiner.Categoria.EXPORTACAO)),
    )
    movimentacoes = Movimentacao.objects.aggregate(
        total=Count("id"),
        em_andamento=Count("id", filter=Q(data_fim__isnull=True)),
    )
    return {
        "clientes": Cliente.objects.count(),
        "conteineres": conteineres,
        "movimentacoes": movimentacoes,
    }


def movimentacoes_por_tipo() -> list[dict]:
    contagem = dict(Movimentacao.objects.values_list("tipo").annotate(total=Count("id")))
    return [
        {"tipo": valor, "label": label, "total": contagem.get(valor, 0)} for valor, label in Movimentacao.Tipo.choices
    ]


def movimentacoes_por_dia(dias: int = 30) -> list[dict]:
    hoje = timezone.localdate()
    inicio = hoje - timedelta(days=dias - 1)
    contagem = dict(
        Movimentacao.objects.filter(data_inicio__date__gte=inicio)
        .annotate(dia=TruncDate("data_inicio"))
        .values_list("dia")
        .annotate(total=Count("id"))
    )
    return [
        {"dia": (inicio + timedelta(days=i)).isoformat(), "total": contagem.get(inicio + timedelta(days=i), 0)}
        for i in range(dias)
    ]


def relatorio_por_cliente() -> list[dict]:
    """Tabela dinâmica: uma linha por cliente, uma coluna por tipo de movimentação."""
    tipos = [valor for valor, _ in Movimentacao.Tipo.choices]
    agregados = {
        tipo: Count("conteineres__movimentacoes", filter=Q(conteineres__movimentacoes__tipo=tipo)) for tipo in tipos
    }
    clientes = Cliente.objects.annotate(
        total=Count("conteineres__movimentacoes"),
        importacao=Count("conteineres", filter=Q(conteineres__categoria=Conteiner.Categoria.IMPORTACAO), distinct=True),
        exportacao=Count("conteineres", filter=Q(conteineres__categoria=Conteiner.Categoria.EXPORTACAO), distinct=True),
        **agregados,
    ).order_by("-total", "nome")
    linhas = []
    for cliente in clientes:
        linhas.append(
            {
                "cliente_id": cliente.pk,
                "cliente": cliente.nome,
                "por_tipo": OrderedDict((tipo, getattr(cliente, tipo)) for tipo in tipos),
                "total": cliente.total,
                "importacao": cliente.importacao,
                "exportacao": cliente.exportacao,
            }
        )
    return linhas
