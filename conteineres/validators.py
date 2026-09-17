"""Validação do código de contêiner segundo a norma ISO 6346.

Formato: AAAU1234567
    - 3 letras: código do proprietário (owner code)
    - 1 letra: identificador de categoria (U = carga, J = equipamento acoplável, Z = trailer/chassi)
    - 6 dígitos: número de série
    - 1 dígito: dígito verificador
"""

import re

from django.core.exceptions import ValidationError

ISO6346_REGEX = re.compile(r"^[A-Z]{3}[UJZ]\d{7}$")


def _letter_values() -> dict[str, int]:
    # Letras valem de 10 a 38, pulando múltiplos de 11 (11, 22, 33).
    values, current = {}, 10
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if current % 11 == 0:
            current += 1
        values[letter] = current
        current += 1
    return values


LETTER_VALUES = _letter_values()


def calcular_digito_verificador(codigo: str) -> int:
    """Calcula o dígito verificador a partir dos 10 primeiros caracteres."""
    codigo = codigo.upper()
    total = 0
    for posicao, char in enumerate(codigo[:10]):
        valor = LETTER_VALUES[char] if char.isalpha() else int(char)
        total += valor * (2**posicao)
    return total % 11 % 10


def is_iso6346_valido(codigo: str) -> bool:
    codigo = (codigo or "").strip().upper()
    if not ISO6346_REGEX.match(codigo):
        return False
    return calcular_digito_verificador(codigo) == int(codigo[10])


def validar_numero_conteiner(codigo: str) -> None:
    codigo = (codigo or "").strip().upper()
    if not ISO6346_REGEX.match(codigo):
        raise ValidationError(
            "Formato inválido. Use 3 letras do proprietário + U, J ou Z + 7 dígitos (ex.: CSQU3054383).",
            code="formato_invalido",
        )
    esperado = calcular_digito_verificador(codigo)
    if esperado != int(codigo[10]):
        raise ValidationError(
            "Dígito verificador inválido (ISO 6346). O dígito esperado é %(esperado)s.",
            code="digito_invalido",
            params={"esperado": esperado},
        )
