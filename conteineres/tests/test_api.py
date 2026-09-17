from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from conteineres.models import Movimentacao

from .factories import criar_cliente, criar_conteiner, criar_movimentacao, criar_usuario


class ApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = criar_usuario()
        cls.cliente = criar_cliente(nome="API Cliente")
        cls.conteiner = criar_conteiner(cliente=cls.cliente, status="cheio")

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_requer_autenticacao(self):
        self.client.force_authenticate(None)
        response = self.client.get(reverse("api-conteiner-list"))
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_listar_e_filtrar_conteineres(self):
        criar_conteiner(status="vazio")
        response = self.client.get(reverse("api-conteiner-list"), {"status": "cheio"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["cliente_nome"], "API Cliente")

    def test_criar_conteiner_valida_iso6346(self):
        payload = {
            "numero": "CSQU3054384",
            "cliente": self.cliente.pk,
            "tipo": "20",
            "status": "vazio",
            "categoria": "importacao",
        }
        response = self.client.post(reverse("api-conteiner-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("numero", response.data)

        payload["numero"] = "csqu3054383"
        response = self.client.post(reverse("api-conteiner-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["numero"], "CSQU3054383")

    def test_criar_movimentacao_valida_datas(self):
        payload = {
            "conteiner": self.conteiner.pk,
            "tipo": "scanner",
            "data_inicio": "2026-01-10T10:00:00-03:00",
            "data_fim": "2026-01-10T09:00:00-03:00",
        }
        response = self.client.post(reverse("api-movimentacao-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("data_fim", response.data)

        payload["data_fim"] = None
        response = self.client.post(reverse("api-movimentacao-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["em_andamento"])

    def test_historico_do_conteiner(self):
        criar_movimentacao(conteiner=self.conteiner)
        criar_movimentacao()
        response = self.client.get(reverse("api-conteiner-movimentacoes", args=[self.conteiner.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_excluir_cliente_com_conteiner_retorna_409(self):
        response = self.client.delete(reverse("api-cliente-detail", args=[self.cliente.pk]))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_relatorio_e_dashboard(self):
        criar_movimentacao(conteiner=self.conteiner, tipo=Movimentacao.Tipo.EMBARQUE)
        relatorio = self.client.get(reverse("api-relatorio"))
        self.assertEqual(relatorio.status_code, 200)
        self.assertEqual(relatorio.data[0]["por_tipo"]["embarque"], 1)

        dashboard = self.client.get(reverse("api-dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.data["indicadores"]["movimentacoes"]["total"], 1)

    def test_schema_openapi(self):
        response = self.client.get(reverse("schema"))
        self.assertEqual(response.status_code, 200)
