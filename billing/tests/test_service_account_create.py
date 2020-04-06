from decimal import Decimal

from django.test import TestCase

from authentication.tests.fixtures import UserFactory
from .. import constants
from ..services import AccountCreateService


class AccountCreateServiceTestCase(TestCase):
    service = AccountCreateService

    def test_create_account(self):
        """Should create account with given user, currency and amount"""
        expected_user = UserFactory()
        expected_currency = constants.USD
        expected_amount = Decimal(100)
        account = self.service.execute(user=expected_user, currency=expected_currency, amount=expected_amount)
        self.assertEqual(account.user, expected_user)
        self.assertEqual(account.currency, expected_currency)
        self.assertEqual(account.amount, expected_amount)
