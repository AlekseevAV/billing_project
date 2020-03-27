from decimal import Decimal

from billing import constants


class ExchangeService:
    # TODO: Where to store exchange rates?
    exchange_rates = {
        # (from, to): rate
        # USD
        (constants.USD, constants.CNY): 0.1,  # USD -> CNY
        (constants.USD, constants.EUR): 0.2,  # USD -> EUR
        # CNY
        (constants.CNY, constants.USD): 0.3,  # CNY -> USD
        (constants.CNY, constants.EUR): 0.4,  # CNY -> EUR
        # EUR
        (constants.EUR, constants.USD): 0.5,  # EUR -> USD
        (constants.EUR, constants.CNY): 0.6,  # EUR -> CNY
    }

    @classmethod
    def execute(cls, from_currency: str, to_currency: str, amount: Decimal) -> Decimal:
        if from_currency == to_currency:
            exchanged_amount = amount
        else:
            exchange_rate = cls.exchange_rates[(from_currency, to_currency)]
            exchanged_amount = amount * exchange_rate
        return exchanged_amount
