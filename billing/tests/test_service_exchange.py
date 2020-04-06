from decimal import Decimal

from unittest import TestCase

from .. import constants
from ..services import ExchangeService


class ExchangeServiceTestCase(TestCase):
    service = ExchangeService

    def test_exchange_same_currency(self):
        """Should return amount without changes"""
        currency = constants.USD
        expected_amount = Decimal(100)
        exchanged_amount = self.service.execute(from_currency=currency, to_currency=currency, amount=expected_amount)
        self.assertEqual(exchanged_amount, expected_amount)

    def test_exchange_different_currencies(self):
        """Should exchange given amount by exchange_rates"""
        exchange_cases = (
            # from currency, to currency, amount
            (constants.USD, constants.CNY, Decimal(100)),  # USD -> CNY
            (constants.USD, constants.EUR, Decimal(100)),  # USD -> EUR
            (constants.CNY, constants.USD, Decimal(100)),  # CNY -> USD
            (constants.CNY, constants.EUR, Decimal(100)),  # CNY -> EUR
            (constants.EUR, constants.USD, Decimal(100)),  # EUR -> USD
            (constants.EUR, constants.CNY, Decimal(100)),  # EUR -> CNY
        )
        for from_currency, to_currency, amount in exchange_cases:
            with self.subTest(from_currency=from_currency, to_currency=to_currency, amount=amount):
                expected_amount = amount * self.service.exchange_rates[(from_currency, to_currency)]
                exchanged_amount = self.service.execute(
                    from_currency=from_currency, to_currency=to_currency, amount=amount)
                self.assertEqual(exchanged_amount, expected_amount)
