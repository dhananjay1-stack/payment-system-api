import uuid
from django.db import models
from django.conf import settings
from banking.models import BankAccount


class Transaction(models.Model):
    """
    Records every payment attempt with its result.
    Stores balance snapshots for audit trail.
    """
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_id = models.CharField(max_length=30, unique=True, editable=False)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_transactions',
    )
    sender_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='outgoing_transactions',
    )
    receiver_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incoming_transactions',
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True, default='')
    failure_reason = models.CharField(max_length=255, blank=True, default='')

    # Balance snapshots for audit
    sender_balance_before = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    sender_balance_after = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    receiver_balance_before = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    receiver_balance_after = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', '-created_at']),
            models.Index(fields=['reference_id']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate a unique reference ID
        if not self.reference_id:
            import time
            self.reference_id = f"TXN{int(time.time() * 1000)}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_id} | {self.amount} | {self.status}"
