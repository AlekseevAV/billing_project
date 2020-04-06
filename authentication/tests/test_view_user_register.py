from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class UserRegisterAPIViewTestCase(TestCase):
    view_name = 'api:v1:authentication:registration'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.client = APIClient()

    def test_resolve_url(self):
        expected_url = '/api/v1/authentication/registration/'
        self.assertEqual(reverse(self.view_name), expected_url)

    def test_user_create(self):
        """Should return user token"""
        response = self.client.post(
            reverse(self.view_name), {'username': 'test_user', 'password': 'pass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(response.json(), {'token': Token.objects.last().key})
