from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from authentication.tests.fixtures import UserFactory
from .fixtures import AccountFactory, TransactionFactory
from .. import constants
from ..utils import set_current_timezone


class AccountsViewTestCase(TestCase):
    list_view_url_name = 'api:v1:billing:accounts-list'
    detail_view_url_name = 'api:v1:billing:accounts-detail'
    transactions_list_view_url_name = 'api:v1:billing:accounts-transactions'
    available_views_names = [list_view_url_name, detail_view_url_name, transactions_list_view_url_name]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.force_authenticate(user=cls.user)

    def test_resolve_url(self):
        """Should resolve url by names"""
        cases = (
            # view_name, expected url, kwargs
            (self.list_view_url_name, '/api/v1/billing/accounts/', None),
            (self.detail_view_url_name, '/api/v1/billing/accounts/1/', {'pk': 1}),
            (self.transactions_list_view_url_name, '/api/v1/billing/accounts/1/transactions/', {'pk': 1}),
        )
        for view_name, expected_url, kwargs in cases:
            with self.subTest(view_name=view_name, expected_url=expected_url, kwargs=kwargs):
                self.assertEqual(reverse(view_name, kwargs=kwargs), expected_url)

    def test_unauthorised_request(self):
        """Should return 401 on unauthorised requests"""
        unauthorised_client = APIClient()
        for url_name in self.available_views_names:
            with self.subTest(url_name=url_name):
                response = unauthorised_client.get(path=reverse(self.list_view_url_name))
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_allowed_methods(self):
        """Should return 405 for not allowed methods"""
        account = AccountFactory(user=self.user)
        available_urls = (
            reverse(self.list_view_url_name),
            reverse(self.detail_view_url_name, kwargs={'pk': account.id}),
            reverse(self.transactions_list_view_url_name, kwargs={'pk': account.id}),
        )
        for method in ['put', 'post', 'patch']:
            for url in available_urls:
                with self.subTest(method=method, url=url):
                    client_method = getattr(self.api_client, method)
                    response = client_method(path=url)
                    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_view(self):
        """Should return list of user accounts"""
        now = timezone.now()
        currency = constants.USD
        amount = Decimal(100)
        user_accounts = AccountFactory.create_batch(
            3, currency=currency, amount=amount, user=self.user, created=now, modified=now)
        AccountFactory.create_batch(2)
        response = self.api_client.get(path=reverse(self.list_view_url_name))
        expected_response_data = []
        for account in sorted(user_accounts, key=lambda acc: acc.id, reverse=True):
            expected_response_data.append({
                'id': account.id,
                'created': set_current_timezone(now).isoformat(),
                'modified': set_current_timezone(now).isoformat(),
                'currency': currency,
                'amount': '{:.2f}'.format(amount),
                'user': self.user.id
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_data)

    def test_detail_view_user_account(self):
        """Should return detail info about user account"""
        now = timezone.now()
        currency = constants.USD
        amount = Decimal(100)
        account = AccountFactory(currency=currency, amount=amount, user=self.user, created=now, modified=now)
        response = self.api_client.get(path=reverse(self.detail_view_url_name, kwargs={'pk': account.id}))
        expected_response_data = {
            'id': account.id,
            'created': set_current_timezone(now).isoformat(),
            'modified': set_current_timezone(now).isoformat(),
            'currency': currency,
            'amount': '{:.2f}'.format(amount),
            'user': self.user.id
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_data)

    def test_detail_view_non_user_account(self):
        """Should return 404 on access non user account"""
        account = AccountFactory()
        response = self.api_client.get(path=reverse(self.detail_view_url_name, kwargs={'pk': account.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_transactions_list_view(self):
        from_account = AccountFactory()
        to_account = AccountFactory(user=self.user)
        amount = Decimal(100)
        commission = Decimal(10)
        now = timezone.now()
        account_transactions = TransactionFactory.create_batch(
            3, from_account=from_account, to_account=to_account, amount=amount, commission=commission,
            created=now, modified=now
        )
        response = self.api_client.get(path=reverse(self.transactions_list_view_url_name, kwargs={'pk': to_account.id}))
        expected_response_data = []
        for transaction in sorted(account_transactions, key=lambda tr: tr.id):
            expected_response_data.append({
                'id': transaction.id,
                'created': set_current_timezone(now).isoformat(),
                'modified': set_current_timezone(now).isoformat(),
                'amount': '{:.2f}'.format(amount),
                'commission': '{:.2f}'.format(commission),
                'from_account': from_account.id,
                'to_account': to_account.id,
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.maxDiff = None
        self.assertEqual(response.json(), expected_response_data)

    def test_transactions_list_view_ordering(self):
        now = timezone.now()
        to_account = AccountFactory(user=self.user)
        transactions = [
            TransactionFactory(
                to_account=to_account, amount=Decimal(10), commission=Decimal(10),
                created=now + timezone.timedelta(days=1), modified=now + timezone.timedelta(days=1)),
            TransactionFactory(
                to_account=to_account, amount=Decimal(20), commission=Decimal(20),
                created=now + timezone.timedelta(days=2), modified=now + timezone.timedelta(days=2)),
            TransactionFactory(
                to_account=to_account, amount=Decimal(30), commission=Decimal(30),
                created=now + timezone.timedelta(days=3), modified=now + timezone.timedelta(days=3)),
        ]
        list_url = reverse(self.transactions_list_view_url_name, kwargs={'pk': to_account.id})
        cases = (
            # ordering field name, expected order
            ('id', sorted(transactions, key=lambda tr: tr.id)),
            ('-id', sorted(transactions, key=lambda tr: tr.id, reverse=True)),
            ('amount', sorted(transactions, key=lambda tr: tr.amount)),
            ('-amount', sorted(transactions, key=lambda tr: tr.amount, reverse=True)),
            ('commission', sorted(transactions, key=lambda tr: tr.commission)),
            ('-commission', sorted(transactions, key=lambda tr: tr.commission, reverse=True)),
            ('created', sorted(transactions, key=lambda tr: tr.created)),
            ('-created', sorted(transactions, key=lambda tr: tr.created, reverse=True)),
            ('modified', sorted(transactions, key=lambda tr: tr.modified)),
            ('-modified', sorted(transactions, key=lambda tr: tr.modified, reverse=True)),
        )
        for ordering_field_name, expected_order in cases:
            expected_order_ids = [acc.id for acc in expected_order]
            with self.subTest(ordering_field_name=ordering_field_name, expected_order_ids=expected_order_ids):
                response = self.api_client.get(path=f'{list_url}?ordering={ordering_field_name}')
                response_accounts_ids = [acc['id'] for acc in response.json()]
                self.assertEqual(response_accounts_ids, expected_order_ids)

    def test_transaction_list_view_filtering(self):
        # TODO: add tests
        self.skipTest('TODO')
