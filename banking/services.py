from django.db import models
from .models import BankAccount

MAX_ACCOUNTS_PER_USER = 3


def check_account_limit(user):
    """
    Returns True if the user can add a new bank account,
    False if they've reached the 3-account limit.
    """
    current_count = BankAccount.objects.filter(user=user, is_active=True).count()
    return current_count < MAX_ACCOUNTS_PER_USER


def top_up_account(account, amount):
    """
    Increases balance of the given bank account.
    Uses F() expression to avoid race conditions.
    """
    from django.db.models import F
    BankAccount.objects.filter(pk=account.pk).update(
        balance=F('balance') + amount
    )
    account.refresh_from_db()
    return account
