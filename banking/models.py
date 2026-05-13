import uuid
from django.db import models
from django.conf import settings


class BankAccount(models.Model):
    """
    Represents a user's bank account.
    Each user can have a maximum of 3 accounts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_accounts',
    )
    account_number = models.CharField(max_length=20, unique=True)
    bank_name = models.CharField(max_length=100)
    account_type = models.CharField(
        max_length=10,
        choices=[('savings', 'Savings'), ('current', 'Current')],
        default='savings',
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bank_accounts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['account_number']),
        ]

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.user.username})"
