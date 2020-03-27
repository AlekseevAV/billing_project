from django.urls import path

from .views import UserAccountsView, AccountTransactionsView


urlpatterns = [
    path('accounts/', UserAccountsView.as_view()),
    path('accounts/<int:account_id>/transactions', AccountTransactionsView.as_view()),
]
