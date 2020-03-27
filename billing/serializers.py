from rest_framework import serializers

from .models import Account, Transaction


class AccountSerializer(serializers.ModelField):
    class Meta:
        model = Account
        fields = '__all__'


class TransactionSerializer(serializers.ModelField):
    class Meta:
        model = Transaction
        fields = '__all__'
