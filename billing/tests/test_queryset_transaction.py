from django.test import TestCase

from .fixtures import TransactionFactory
from ..models import Transaction


class TransactionQuerySetTestCase(TestCase):

    def test_by_account_filter_from_account(self):
        """Should return transactions by account filtered by from_account and to_account fields"""
        expected_transaction = TransactionFactory()
        TransactionFactory.create_batch(5)
        for filter_field in ['from_account', 'to_account']:
            with self.subTest('Filter transactions by field', filter_field=filter_field):
                filtered_transactions = Transaction.objects.by_account(
                    account=getattr(expected_transaction, filter_field))
                self.assertEqual(filtered_transactions.count(), 1)
                self.assertEqual(filtered_transactions.last(), expected_transaction)
