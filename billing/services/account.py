from decimal import Decimal

from django.contrib.auth import get_user_model

from billing.models import Account

User = get_user_model()


class AccountCreateService:
    @classmethod
    def execute(cls, user: User, currency: str, amount: Decimal) -> Account:
        return Account.objects.create(user=user, currency=currency, amount=amount)
