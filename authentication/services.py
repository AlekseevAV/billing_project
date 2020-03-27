from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction

from billing import constants
from billing.services import AccountCreateService

User = get_user_model()


class UserRegistrationService:
    account_create_service = AccountCreateService
    pre_created_accounts_for_new_users = {
        # currency: amount
        constants.USD: Decimal(100.),
        constants.CNY: Decimal(0.),
        constants.EUR: Decimal(0.),
    }

    @classmethod
    def execute(cls, username: str, password: str) -> User:
        """Create new user"""
        with transaction.atomic():
            user = cls.create_user(username=username, password=password)
            cls.create_accounts(user=user)
            return user

    @classmethod
    def create_user(cls, username: str, password: str) -> User:
        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def create_accounts(cls, user: User):
        for currency, amount in cls.pre_created_accounts_for_new_users.values():
            cls.account_create_service.execute(user=user, currency=currency, amount=amount)
