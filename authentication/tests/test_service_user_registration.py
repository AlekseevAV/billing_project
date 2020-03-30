from django.contrib.auth import get_user_model
from django.test import TestCase

from ..services import UserRegistrationService

User = get_user_model()


class UserRegistrationServiceTestCase(TestCase):
    user_registration_service = UserRegistrationService

    def test_create_user(self):
        """Should create user"""
        username = 'some_username'
        self.user_registration_service.execute(username=username, password='pass')
        last_created_user = User.objects.last()
        self.assertEqual(last_created_user.username, username)

    def test_create_user_accounts(self):
        """Should create accounts for new user with given amounts"""
        self.user_registration_service.execute(username='username', password='pass')
        last_created_user = User.objects.last()
        for currency, amount in self.user_registration_service.pre_created_accounts_for_new_users.items():
            with self.subTest('Test exist pre created user account', currency=currency, amount=amount):
                self.assertTrue(last_created_user.accounts.filter(currency=currency, amount=amount).exists())
