from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from authentication.tests.fixtures import UserFactory
from .fixtures import AccountFactory, TransactionFactory
from .. import constants
from ..models import Transaction
from ..utils import set_current_timezone


class TransactionsViewTestCase(TestCase):
    create_url_name = 'api:v1:billing:transactions-list'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.force_authenticate(user=cls.user)

    def test_resolve_url(self):
        """Should resolve url by names"""
        self.assertEqual(reverse(self.create_url_name), '/api/v1/billing/transactions/')

    def test_unauthorised_request(self):
        """Should return 401 on unauthorised requests"""
        unauthorised_client = APIClient()
        response = unauthorised_client.get(path=reverse(self.create_url_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_allowed_methods(self):
        """Should return 405 for not allowed methods"""
        url = reverse(self.create_url_name)
        for method in ['get', 'patch']:
            with self.subTest(method=method):
                client_method = getattr(self.api_client, method)
                response = client_method(path=url)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_request(self):
        """Should create transaction"""
        response = self.api_client.post(path=reverse(self.create_url_name), data={
            'from_account': AccountFactory().id, 'to_account': AccountFactory().id, 'amount': Decimal(10)
        })
        last_transaction = Transaction.objects.last()
        expected_response_data = {
            'amount': '{:.2f}'.format(last_transaction.amount),
            'from_account': last_transaction.from_account.id,
            'to_account': last_transaction.to_account.id,
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), expected_response_data)
