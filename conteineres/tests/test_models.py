from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from conteineres import services
from conteineres.models import Conteiner, Movimentacao

from .factories import criar_cliente, criar_conteiner, criar_movimentacao


class ConteinerModelTests(TestCase):
    def test_numero_salvo_em_maiusculas(self):
        conteiner = criar_conteiner(numero="csqu3054383")
        self.assertEqual(conteiner.numero, "CSQU3054383")

    def test_full_clean_rejeita_numero_invalido(self):
        conteiner = Conteiner(
            numero="CSQU3054384", cliente=criar_cliente(), tipo="20", status="cheio", categoria="importacao"
        )
        with self.assertRaises(ValidationError) as ctx:
            conteiner.full_clean()
        self.assertIn("numero", ctx.exception.message_dict)

    def test_cliente_com_conteiner_nao_pode_ser_excluido(self):
        conteiner = criar_conteiner()
        with self.assertRaises(ProtectedError):
            conteiner.cliente.delete()

    def test_excluir_conteiner_remove_movimentacoes(self):
        mov = criar_movimentacao()
        mov.conteiner.delete()
        self.assertFalse(Movimentacao.objects.exists())


class MovimentacaoModelTests(TestCase):
    def test_clean_rejeita_fim_antes_do_inicio(self):
        agora = timezone.now()
        mov = Movimentacao(
            conteiner=criar_conteiner(), tipo="pesagem", data_inicio=agora, data_fim=agora - timedelta(minutes=1)
        )
        with self.assertRaises(ValidationError) as ctx:
            mov.full_clean()
        self.assertIn("data_fim", ctx.exception.message_dict)

    def test_constraint_no_banco(self):
        agora = timezone.now()
        with self.assertRaises(IntegrityError), transaction.atomic():
            criar_movimentacao(data_inicio=agora, data_fim=agora - timedelta(hours=1))

    def test_em_andamento(self):
        mov = criar_movimentacao(data_fim=None)
        self.assertTrue(mov.em_andamento)
        self.assertEqual(Movimentacao.objects.em_andamento().count(), 1)
        self.assertEqual(Movimentacao.objects.finalizadas().count(), 0)


class ServicesTests(TestCase):
    def test_relatorio_por_cliente_agrupa_corretamente(self):
        cliente = criar_cliente(nome="ACME")
        c1 = criar_conteiner(cliente=cliente, categoria="importacao")
        c2 = criar_conteiner(cliente=cliente, categoria="exportacao")
        criar_movimentacao(conteiner=c1, tipo="scanner")
        criar_movimentacao(conteiner=c1, tipo="scanner")
        criar_movimentacao(conteiner=c2, tipo="embarque")
        criar_cliente(nome="Sem movimentação")

        linhas = {linha["cliente"]: linha for linha in services.relatorio_por_cliente()}

        acme = linhas["ACME"]
        self.assertEqual(acme["total"], 3)
        self.assertEqual(acme["por_tipo"]["scanner"], 2)
        self.assertEqual(acme["por_tipo"]["embarque"], 1)
        self.assertEqual(acme["importacao"], 1)
        self.assertEqual(acme["exportacao"], 1)
        self.assertEqual(linhas["Sem movimentação"]["total"], 0)

    def test_indicadores_gerais(self):
        criar_movimentacao(data_fim=None, conteiner=criar_conteiner(status="vazio"))
        criar_movimentacao()
        dados = services.indicadores_gerais()
        self.assertEqual(dados["conteineres"]["total"], 2)
        self.assertEqual(dados["conteineres"]["vazios"], 1)
        self.assertEqual(dados["movimentacoes"]["total"], 2)
        self.assertEqual(dados["movimentacoes"]["em_andamento"], 1)

    def test_movimentacoes_por_dia_retorna_serie_completa(self):
        criar_movimentacao(data_inicio=timezone.now(), data_fim=None)
        serie = services.movimentacoes_por_dia(7)
        self.assertEqual(len(serie), 7)
        self.assertEqual(serie[-1]["total"], 1)
