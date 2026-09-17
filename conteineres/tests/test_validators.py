from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from conteineres.validators import calcular_digito_verificador, is_iso6346_valido, validar_numero_conteiner


class ISO6346Tests(SimpleTestCase):
    def test_codigos_validos(self):
        for codigo in ["CSQU3054383", "MSKU9070323", "TGHU8420199"]:
            with self.subTest(codigo=codigo):
                self.assertTrue(is_iso6346_valido(codigo))

    def test_calcula_digito_verificador(self):
        self.assertEqual(calcular_digito_verificador("CSQU305438"), 3)

    def test_aceita_minusculas_e_espacos(self):
        self.assertTrue(is_iso6346_valido("  csqu3054383 "))

    def test_digito_verificador_incorreto(self):
        with self.assertRaisesMessage(ValidationError, "Dígito verificador inválido"):
            validar_numero_conteiner("CSQU3054384")

    def test_formatos_invalidos(self):
        for codigo in ["", "CSQU305438", "CSQX3054383", "C5QU3054383", "CSQU30543833", "TEST1234567"]:
            with self.subTest(codigo=codigo):
                self.assertFalse(is_iso6346_valido(codigo))
                with self.assertRaises(ValidationError):
                    validar_numero_conteiner(codigo)
