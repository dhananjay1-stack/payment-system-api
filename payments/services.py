from decimal import Decimal
from django.db import transaction as db_transaction
from django.db.models import F
from banking.models import BankAccount
from .models import Transaction


def process_payment(sender, sender_account_id, receiver_account_number, amount, remarks=''):
    """
    Handles the full payment flow atomically:
    1. Validates sender owns the account
    2. Validates receiver account exists
    3. Checks sufficient balance
    4. Transfers funds within a DB transaction
    5. Creates a Transaction record (SUCCESS or FAILED)

    Returns the Transaction object.
    """
    amount = Decimal(str(amount))

    # --- Validate sender account ---
    try:
        sender_account = BankAccount.objects.get(
            pk=sender_account_id, user=sender, is_active=True
        )
    except BankAccount.DoesNotExist:
        return _create_failed_transaction(
            sender=sender,
            sender_account=None,
            receiver_account=None,
            amount=amount,
            remarks=remarks,
            failure_reason="Sender account not found or does not belong to you.",
        )

    # --- Validate receiver account ---
    try:
        receiver_account = BankAccount.objects.get(
            account_number=receiver_account_number, is_active=True
        )
    except BankAccount.DoesNotExist:
        return _create_failed_transaction(
            sender=sender,
            sender_account=sender_account,
            receiver_account=None,
            amount=amount,
            remarks=remarks,
            failure_reason="Receiver account not found or inactive.",
        )

    # --- Prevent self-transfer ---
    if sender_account.pk == receiver_account.pk:
        return _create_failed_transaction(
            sender=sender,
            sender_account=sender_account,
            receiver_account=receiver_account,
            amount=amount,
            remarks=remarks,
            failure_reason="Cannot transfer to the same account.",
        )

    # --- Check balance ---
    if sender_account.balance < amount:
        return _create_failed_transaction(
            sender=sender,
            sender_account=sender_account,
            receiver_account=receiver_account,
            amount=amount,
            remarks=remarks,
            failure_reason="Insufficient balance.",
            sender_balance_before=sender_account.balance,
        )

    # --- Execute atomic transfer ---
    with db_transaction.atomic():
        # Lock rows to prevent race conditions
        sender_acc = BankAccount.objects.select_for_update().get(pk=sender_account.pk)
        receiver_acc = BankAccount.objects.select_for_update().get(pk=receiver_account.pk)

        # Double-check balance after locking
        if sender_acc.balance < amount:
            return _create_failed_transaction(
                sender=sender,
                sender_account=sender_acc,
                receiver_account=receiver_acc,
                amount=amount,
                remarks=remarks,
                failure_reason="Insufficient balance (concurrent check).",
                sender_balance_before=sender_acc.balance,
            )

        sender_balance_before = sender_acc.balance
        receiver_balance_before = receiver_acc.balance

        # Update balances using F() for safety
        BankAccount.objects.filter(pk=sender_acc.pk).update(
            balance=F('balance') - amount
        )
        BankAccount.objects.filter(pk=receiver_acc.pk).update(
            balance=F('balance') + amount
        )

        sender_balance_after = sender_balance_before - amount
        receiver_balance_after = receiver_balance_before + amount

        txn = Transaction.objects.create(
            sender=sender,
            sender_account=sender_acc,
            receiver_account=receiver_acc,
            amount=amount,
            status='SUCCESS',
            remarks=remarks,
            sender_balance_before=sender_balance_before,
            sender_balance_after=sender_balance_after,
            receiver_balance_before=receiver_balance_before,
            receiver_balance_after=receiver_balance_after,
        )

    return txn


def _create_failed_transaction(sender, sender_account, receiver_account,
                                amount, remarks, failure_reason,
                                sender_balance_before=None):
    """Helper to create a FAILED transaction record."""
    return Transaction.objects.create(
        sender=sender,
        sender_account=sender_account,
        receiver_account=receiver_account,
        amount=amount,
        status='FAILED',
        remarks=remarks,
        failure_reason=failure_reason,
        sender_balance_before=sender_balance_before,
    )
