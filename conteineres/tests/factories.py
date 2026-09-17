from datetime import timedelta
from itertools import count

from django.contrib.auth import get_user_model
from django.utils import timezone

from conteineres.models import Cliente, Conteiner, Movimentacao
from conteineres.validators import calcular_digito_verificador

_seq = count(1)


def numero_valido(owner: str = "TST") -> str:
    base = f"{owner}U{next(_seq):06d}"
    return f"{base}{calcular_digito_verificador(base)}"


def criar_usuario(username: str = "tester", password: str = "senha-forte-123"):
    return get_user_model().objects.create_user(username=username, password=password)


def criar_cliente(**kwargs) -> Cliente:
    kwargs.setdefault("nome", f"Cliente {next(_seq)}")
    return Cliente.objects.create(**kwargs)


def criar_conteiner(**kwargs) -> Conteiner:
    kwargs.setdefault("numero", numero_valido())
    if "cliente" not in kwargs:
        kwargs["cliente"] = criar_cliente()
    kwargs.setdefault("tipo", Conteiner.Tipo.VINTE)
    kwargs.setdefault("status", Conteiner.Status.CHEIO)
    kwargs.setdefault("categoria", Conteiner.Categoria.IMPORTACAO)
    return Conteiner.objects.create(**kwargs)


def criar_movimentacao(**kwargs) -> Movimentacao:
    if "conteiner" not in kwargs:
        kwargs["conteiner"] = criar_conteiner()
    kwargs.setdefault("tipo", Movimentacao.Tipo.GATE_IN)
    kwargs.setdefault("data_inicio", timezone.now() - timedelta(hours=2))
    kwargs.setdefault("data_fim", timezone.now() - timedelta(hours=1))
    return Movimentacao.objects.create(**kwargs)
