"""Regras de negócio e formato das mensagens do conversor de moedas."""

from __future__ import annotations

import json
import random
import re
import unicodedata
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


CURRENCIES: dict[str, tuple[str, Decimal, Decimal]] = {
    "USD": ("dólar americano", Decimal("4.80"), Decimal("6.20")),
    "EUR": ("euro", Decimal("5.20"), Decimal("6.80")),
    "GBP": ("libra esterlina", Decimal("6.10"), Decimal("8.20")),
    "JPY": ("iene japonês", Decimal("0.030"), Decimal("0.045")),
    "ARS": ("peso argentino", Decimal("0.003"), Decimal("0.010")),
}

ALIASES = {
    "usd": "USD", "dolar": "USD", "dolar americano": "USD",
    "eur": "EUR", "euro": "EUR",
    "gbp": "GBP", "libra": "GBP", "libra esterlina": "GBP",
    "jpy": "JPY", "iene": "JPY", "iene japones": "JPY",
    "ars": "ARS", "peso": "ARS", "peso argentino": "ARS",
}


def _without_accents(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


def parse_brl(value: Any) -> Decimal:
    """Converte uma entrada monetária brasileira em Decimal positivo."""
    if isinstance(value, bool):
        raise ValueError("O valor deve ser numérico.")
    text = str(value).strip().lower().replace("r$", "").replace(" ", "")
    if not text:
        raise ValueError("O valor não pode ser vazio.")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        raise ValueError("Valor inválido. Exemplos aceitos: 10, 10,50 ou R$ 10,50.")
    try:
        amount = Decimal(text)
    except InvalidOperation as error:
        raise ValueError("O valor deve ser numérico.") from error
    if amount <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    return amount


def normalize_currency(value: Any) -> str:
    key = _without_accents(str(value).strip().lower())
    try:
        return ALIASES[key]
    except KeyError as error:
        choices = ", ".join(CURRENCIES)
        raise ValueError(f"Moeda não suportada. Use uma destas: {choices}.") from error


def random_rate(code: str, rng: random.Random | None = None) -> Decimal:
    """Gera uma cotação simulada com quatro casas decimais."""
    generator = rng or random
    _, minimum, maximum = CURRENCIES[code]
    rate = minimum + (maximum - minimum) * Decimal(str(generator.random()))
    return rate.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def convert_request(request: dict[str, Any], rng: random.Random | None = None) -> dict[str, Any]:
    """Valida a requisição e produz uma resposta serializável em JSON."""
    try:
        amount = parse_brl(request.get("valor", ""))
        code = normalize_currency(request.get("moeda", ""))
        rate = random_rate(code, rng)
        converted = (amount / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "ok": True,
            "valor_brl": str(amount.quantize(Decimal("0.01"))),
            "moeda": code,
            "nome_moeda": CURRENCIES[code][0],
            "cotacao": str(rate),
            "valor_convertido": str(converted),
        }
    except (ValueError, AttributeError) as error:
        return {"ok": False, "erro": str(error)}


def encode_message(message: dict[str, Any]) -> bytes:
    return json.dumps(message, ensure_ascii=False).encode("utf-8")


def decode_message(data: bytes) -> dict[str, Any]:
    try:
        message = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Mensagem JSON inválida.") from error
    if not isinstance(message, dict):
        raise ValueError("A mensagem deve ser um objeto JSON.")
    return message


def format_response(response: dict[str, Any]) -> str:
    if not response.get("ok"):
        return f"Erro: {response.get('erro', 'erro desconhecido')}"
    return (
        f"R$ {response['valor_brl']} = {response['valor_convertido']} {response['moeda']}\n"
        f"Cotação simulada: 1 {response['moeda']} = R$ {response['cotacao']}"
    )
