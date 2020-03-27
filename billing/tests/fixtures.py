from decimal import Decimal

import factory

from authentication.tests.fixtures import UserFactory
from billing import constants
from billing.models import Account, Transaction


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    currency = constants.USD
    amount = Decimal(100.)


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    from_account = factory.SubFactory(AccountFactory)
    to_account = factory.SubFactory(AccountFactory)
    amount = Decimal(100.)
    currency = constants.USD
