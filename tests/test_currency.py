import random
import unittest
from decimal import Decimal

from currency import convert_request, decode_message, encode_message, normalize_currency, parse_brl


class CurrencyTests(unittest.TestCase):
    def test_parse_brazilian_values(self):
        self.assertEqual(parse_brl("R$ 10,50"), Decimal("10.50"))
        self.assertEqual(parse_brl("1.234,56"), Decimal("1234.56"))

    def test_normalize_currency_with_accents(self):
        self.assertEqual(normalize_currency("dólar"), "USD")
        self.assertEqual(normalize_currency("LIBRA"), "GBP")

    def test_conversion_is_consistent_with_rate(self):
        result = convert_request({"valor": "100", "moeda": "euro"}, random.Random(7))
        self.assertTrue(result["ok"])
        expected = (Decimal("100") / Decimal(result["cotacao"])).quantize(Decimal("0.01"))
        self.assertEqual(Decimal(result["valor_convertido"]), expected)

    def test_invalid_request_returns_error(self):
        result = convert_request({"valor": "-10", "moeda": "bitcoin"})
        self.assertFalse(result["ok"])
        self.assertIn("Valor inválido", result["erro"])

    def test_json_round_trip_keeps_unicode(self):
        message = {"valor": "10", "moeda": "dólar"}
        self.assertEqual(decode_message(encode_message(message)), message)


if __name__ == "__main__":
    unittest.main()
