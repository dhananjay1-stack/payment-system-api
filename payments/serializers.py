from rest_framework import serializers
from .models import Transaction


class PaymentSerializer(serializers.Serializer):
    """Validates incoming payment request data."""
    sender_account_id = serializers.UUIDField()
    receiver_account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    remarks = serializers.CharField(max_length=255, required=False, default='')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be positive.")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    """Read serializer for transaction details."""
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_account_number = serializers.CharField(
        source='sender_account.account_number', read_only=True, default=None
    )
    receiver_account_number = serializers.CharField(
        source='receiver_account.account_number', read_only=True, default=None
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference_id', 'sender_username',
            'sender_account_number', 'receiver_account_number',
            'amount', 'status', 'remarks', 'failure_reason',
            'sender_balance_before', 'sender_balance_after',
            'receiver_balance_before', 'receiver_balance_after',
            'created_at',
        ]
        read_only_fields = fields
