import threading
from decimal import Decimal

from django.test import TestCase, override_settings

from .fixtures import AccountFactory
from .. import constants
from ..models import Account
from ..services import TransactionCreateService, TransactionCreateError


class TransactionCreateServiceTestCase(TestCase):
    service = TransactionCreateService
    transfer_commission_rate = Decimal(0.1)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.account_from = AccountFactory(currency=constants.USD, amount=Decimal(100))
        cls.account_to = AccountFactory(currency=constants.USD, amount=Decimal(100))

    def test_successfully_transaction_create(self):
        """Should create transaction and change accounts amount"""
        transaction = self.service(
            from_account=self.account_from, to_account=self.account_to, amount=Decimal(10)).execute()
        account_from = Account.objects.get(id=self.account_from.id)
        account_to = Account.objects.get(id=self.account_to.id)
        self.assertEqual(transaction.from_account, account_from)
        self.assertEqual(transaction.to_account, account_to)
        self.assertEqual(account_from.amount, Decimal(90))
        self.assertEqual(account_to.amount, Decimal(110))

    def test_create_with_negative_amount(self):
        """Should raise exception if amount is negative number"""
        with self.assertRaisesMessage(TransactionCreateError, 'Amount should be grater then 0'):
            self.service(from_account=self.account_from, to_account=self.account_to, amount=Decimal(-10)).execute()

    def test_create_if_account_from_has_no_money(self):
        """Should raise exception if account_from don't have enough money"""
        with self.assertRaisesMessage(TransactionCreateError, f'Not enough amount in account {self.account_from}'):
            self.service(from_account=self.account_from, to_account=self.account_to, amount=Decimal(1000)).execute()

    def test_create_transaction_with_same_account(self):
        """Should raise exception to create transaction with same accounts"""
        with self.assertRaisesMessage(TransactionCreateError, 'Transaction to same account not allowed'):
            self.service(from_account=self.account_from, to_account=self.account_from, amount=Decimal(10)).execute()

    def test_get_commission_for_same_accounts(self):
        """Should return zero commission if both accounts belong to one user"""
        second_user_account = AccountFactory(user=self.account_from.user)
        commission = self.service(
            from_account=self.account_from, to_account=second_user_account, amount=Decimal(10)).get_commission()
        self.assertEqual(commission, Decimal(0))

    @override_settings(TRANSFER_COMMISSION_RATE=transfer_commission_rate)
    def test_get_commission_for_different_accounts(self):
        """Should return expected transfer commission"""
        amount = Decimal(10.)
        commission = self.service(
            from_account=self.account_from, to_account=self.account_to, amount=amount).get_commission()
        self.assertEqual(commission, amount * self.transfer_commission_rate)

    def test_is_self_transfer(self):
        """Should return True or False if accounts belong to one user"""
        second_user_account = AccountFactory(user=self.account_from.user)
        account_transfer_cases = (
            # account from, account to, expected result
            (self.account_from, self.account_to, False),
            (self.account_from, second_user_account, True),
        )
        for account_from, account_to, expected_result in account_transfer_cases:
            with self.subTest(account_from=account_from, account_to=account_to, expected_result=expected_result):
                service = self.service(from_account=account_from, to_account=account_to, amount=Decimal(10))
                self.assertEqual(service.is_self_transfer, expected_result)
