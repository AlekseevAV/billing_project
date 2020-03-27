from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from .views import UserRegisterAPIView


urlpatterns = [
    path('registration/', UserRegisterAPIView.as_view()),
    path('login/', ObtainAuthToken.as_view()),
]
