from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserRegisterSerializer
from .services import UserRegistrationService

User = get_user_model()


class UserRegisterAPIView(APIView):
    permission_classes = ()
    serializer_class = UserRegisterSerializer
    user_registration_class = UserRegistrationService

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.user_registration_class.execute(
            username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        token = self.create_token_for_user(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

    @staticmethod
    def create_token_for_user(user: User) -> Token:
        token, _ = Token.objects.get_or_create(user=user)
        return token
