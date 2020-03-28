from rest_framework import status
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer, TransactionCreateSerializer
from .services import TransactionCreateService, TransactionCreateError


class AccountsView(ReadOnlyModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    transactions_queryset = Transaction.objects.all()
    transactions_filter_backends = [DjangoFilterBackend, OrderingFilter]
    transactions_serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_transactions_queryset(self):
        account = self.get_object()
        queryset = self.transactions_queryset.by_account(account=account)
        for backend in self.transactions_filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    @action(detail=True)
    def transactions(self, request, *args, **kwargs):
        queryset = self.get_transactions_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.transactions_serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.transactions_serializer_class(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)


class TransactionsView(CreateModelMixin, GenericViewSet):
    serializer_class = TransactionCreateSerializer
    transaction_create_service = TransactionCreateService

    def perform_create(self, serializer):
        transaction = self.transaction_create_service(
            from_account=serializer.validated_data['from_account'], to_account=serializer.validated_data['to_account'],
            amount=serializer.validated_data['amount'])
        transaction.execute()

    def handle_exception(self, exc):
        if isinstance(exc, TransactionCreateError):
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)
