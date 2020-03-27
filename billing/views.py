from django.db.models import Q
from django_filters.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, get_object_or_404

from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer


class UserAccountsView(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class AccountTransactionsView(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def dispatch(self, request, *args, **kwargs):
        self.account = get_object_or_404(Account, id=request.GET.get('account_id'), user=self.request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(Q(from_account=self.account) | Q(to_account=self.account))
