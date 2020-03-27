from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserRegisterSerializer
from .services import UserRegistrationService


class UserRegisterAPIView(APIView):
    serializer_class = UserRegisterSerializer
    user_registration_class = UserRegistrationService

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.user_registration_class.execute(
            username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
