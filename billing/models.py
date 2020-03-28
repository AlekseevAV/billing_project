from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel

from .constants import CURRENCIES

User = get_user_model()


class Account(TimeStampedModel):
    CURRENCIES = Choices(*CURRENCIES)

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='accounts')
    currency = StatusField(choices_name='CURRENCIES')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0), validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'
        ordering = ('-created',)

    def __str__(self):
        return f'Account ({self.currency})'


class TransactionQuerySet(models.QuerySet):
    def by_account(self, account: Account):
        return self.filter(Q(from_account=account) | Q(to_account=account))


class Transaction(TimeStampedModel):
    from_account = models.ForeignKey(
        Account, related_name='outgoing_transactions', on_delete=models.PROTECT, blank=True, null=True)
    to_account = models.ForeignKey(Account, related_name='incoming_transactions', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)

    objects = TransactionQuerySet.as_manager()

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ('-created',)
        index_together = [('from_account', 'to_account')]
