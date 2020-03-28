from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from .exceptions import TransactionCreateError
from .exchange import ExchangeService
from ..models import Account, Transaction

User = get_user_model()


class TransactionCreateService:
    exchange_service = ExchangeService
    # TODO: How to store commission rate?
    commission_rate = settings.TRANSFER_COMMISSION_RATE

    def __init__(self, from_account: Account, to_account: Account, amount: Decimal) -> None:
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount

    @atomic()
    def execute(self) -> Transaction:
        self.block_accounts(from_account_id=self.from_account.id, to_account_id=self.to_account.id)
        self.validate()
        self.proceed_accounts()
        return self.create_transaction()

    def block_accounts(self, from_account_id: int, to_account_id: int) -> None:
        """
        Block and get accounts from DB

        Sort accounts ids to avoid DB deadlocks
        """
        accounts_by_id = {}
        for account in Account.objects.select_for_update().filter(id__in=sorted([from_account_id, to_account_id])):
            accounts_by_id[account.id] = account
        self.from_account = accounts_by_id[from_account_id]
        self.to_account = accounts_by_id[to_account_id]

    def validate(self):
        if self.amount < 0:
            raise TransactionCreateError('Amount should be grater then 0')
        if self.from_account.amount < self.amount:
            raise TransactionCreateError(f'Not enough amount in account {self.from_account}')
        if self.from_account == self.to_account:
            raise TransactionCreateError(f'Transaction to same account not allowed')

    def proceed_accounts(self) -> None:
        # subtract amount from from_account
        self.from_account.amount -= self.amount
        self.from_account.save(update_fields=['amount'])
        # plus amount to to_account
        self.to_account.amount += self.exchange_service.execute(
            from_currency=self.from_account.currency, to_currency=self.to_account.currency, amount=self.amount)
        self.to_account.save(update_fields=['amount'])

    def create_transaction(self) -> Transaction:
        return Transaction.objects.create(
            from_account=self.from_account, to_account=self.to_account, amount=self.amount,
            commission=self.get_commission())

    def get_commission(self) -> Decimal:
        """Calc commission for current transaction"""
        if self.is_self_transfer:
            commission = Decimal(0.)
        else:
            commission = self.amount * self.commission_rate
        return commission

    @property
    def is_self_transfer(self) -> bool:
        """Is transaction between accounts belong to same user"""
        return self.from_account.user == self.to_account.user
