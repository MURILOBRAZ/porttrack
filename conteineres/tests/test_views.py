from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from conteineres.models import Cliente, Conteiner, Movimentacao

from .factories import criar_cliente, criar_conteiner, criar_movimentacao, criar_usuario


class AutenticacaoTests(TestCase):
    def test_paginas_exigem_login(self):
        for nome in ["dashboard", "conteiner_list", "movimentacao_list", "cliente_list", "relatorio"]:
            with self.subTest(pagina=nome):
                response = self.client.get(reverse(nome))
                self.assertRedirects(response, f"{reverse('login')}?next={reverse(nome)}")


class ViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = criar_usuario()
        cls.cliente = criar_cliente(nome="Cliente Teste")
        cls.conteiner = criar_conteiner(cliente=cls.cliente)
        cls.movimentacao = criar_movimentacao(conteiner=cls.conteiner, data_fim=None)

    def setUp(self):
        self.client.force_login(self.user)

    def test_paginas_carregam(self):
        urls = [
            reverse("dashboard"),
            reverse("conteiner_list"),
            reverse("conteiner_list") + "?q=TST&status=cheio",
            reverse("conteiner_detail", args=[self.conteiner.pk]),
            reverse("conteiner_create"),
            reverse("conteiner_update", args=[self.conteiner.pk]),
            reverse("movimentacao_list") + "?em_andamento=true",
            reverse("movimentacao_create") + f"?conteiner={self.conteiner.pk}",
            reverse("cliente_list"),
            reverse("cliente_detail", args=[self.cliente.pk]),
            reverse("relatorio"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_criar_conteiner_valido(self):
        response = self.client.post(
            reverse("conteiner_create"),
            {
                "numero": "csqu3054383",
                "cliente": self.cliente.pk,
                "tipo": "40",
                "status": "vazio",
                "categoria": "exportacao",
            },
        )
        conteiner = Conteiner.objects.get(numero="CSQU3054383")
        self.assertRedirects(response, conteiner.get_absolute_url())

    def test_criar_conteiner_invalido_exibe_erro(self):
        response = self.client.post(
            reverse("conteiner_create"),
            {
                "numero": "CSQU3054380",
                "cliente": self.cliente.pk,
                "tipo": "40",
                "status": "vazio",
                "categoria": "exportacao",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dígito verificador inválido")
        self.assertContains(response, "is-invalid")

    def test_criar_movimentacao_com_datas_invertidas(self):
        response = self.client.post(
            reverse("movimentacao_create"),
            {
                "conteiner": self.conteiner.pk,
                "tipo": "pesagem",
                "data_inicio": "2026-01-10T10:00",
                "data_fim": "2026-01-10T09:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "não pode ser anterior")

    def test_finalizar_movimentacao(self):
        url = reverse("movimentacao_finalizar", args=[self.movimentacao.pk])
        response = self.client.post(url, {"next": "https://site-malicioso.com"})
        self.assertRedirects(response, self.conteiner.get_absolute_url())
        self.movimentacao.refresh_from_db()
        self.assertFalse(self.movimentacao.em_andamento)

    def test_excluir_cliente_protegido(self):
        response = self.client.post(reverse("cliente_delete", args=[self.cliente.pk]), follow=True)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())
        self.assertContains(response, "Não é possível excluir")

    def test_excluir_conteiner(self):
        response = self.client.post(reverse("conteiner_delete", args=[self.conteiner.pk]))
        self.assertRedirects(response, reverse("conteiner_list"))
        self.assertFalse(Movimentacao.objects.exists())

    def test_exportar_csv(self):
        response = self.client.get(reverse("relatorio_csv"))
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        conteudo = response.content.decode("utf-8-sig")
        self.assertIn("Cliente;Embarque", conteudo)
        self.assertIn("Cliente Teste", conteudo)


class SeedDemoTests(TestCase):
    def test_seed_demo_cria_dados_validos(self):
        call_command("seed_demo", conteineres=10, stdout=StringIO())
        self.assertTrue(Conteiner.objects.exists())
        for conteiner in Conteiner.objects.all():
            conteiner.full_clean()
        self.assertTrue(self.client.login(username="demo", password="demo1234"))
