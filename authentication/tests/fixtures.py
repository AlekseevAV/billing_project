import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'User #{}'.format(n))
    first_name = 'Test'
    last_name = 'User'
    is_staff = False
    is_active = True
    is_superuser = False
