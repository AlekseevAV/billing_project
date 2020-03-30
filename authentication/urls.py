from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from .views import UserRegisterAPIView


urlpatterns = [
    path('registration/', UserRegisterAPIView.as_view(), name='registration'),
    path('login/', ObtainAuthToken.as_view(), name='login'),
]
