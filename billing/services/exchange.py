from decimal import Decimal

from billing import constants


# TODO: tests
class ExchangeService:
    # TODO: Where to store exchange rates?
    exchange_rates = {
        # (from, to): rate
        # USD
        (constants.USD, constants.CNY): Decimal(1.),  # USD -> CNY
        (constants.USD, constants.EUR): Decimal(1.),  # USD -> EUR
        # CNY
        (constants.CNY, constants.USD): Decimal(1.),  # CNY -> USD
        (constants.CNY, constants.EUR): Decimal(1.),  # CNY -> EUR
        # EUR
        (constants.EUR, constants.USD): Decimal(1.),  # EUR -> USD
        (constants.EUR, constants.CNY): Decimal(1.),  # EUR -> CNY
    }

    @classmethod
    def execute(cls, from_currency: str, to_currency: str, amount: Decimal) -> Decimal:
        if from_currency == to_currency:
            exchanged_amount = amount
        else:
            exchange_rate = cls.exchange_rates[(from_currency, to_currency)]
            exchanged_amount = amount * exchange_rate
        return exchanged_amount
