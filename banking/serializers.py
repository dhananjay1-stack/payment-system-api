import random
from rest_framework import serializers
from .models import BankAccount
from .services import check_account_limit


def generate_account_number():
    """Generate a random 12-digit account number."""
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])


class BankAccountSerializer(serializers.ModelSerializer):
    """Read serializer for bank account details."""
    owner = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = BankAccount
        fields = ['id', 'owner', 'account_number', 'bank_name',
                  'account_type', 'balance', 'is_active', 'created_at']
        read_only_fields = ['id', 'account_number', 'balance',
                            'is_active', 'created_at']


class BankAccountCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new bank account.
    Auto-generates account number and enforces the 3-account limit.
    """
    class Meta:
        model = BankAccount
        fields = ['id', 'bank_name', 'account_type', 'account_number',
                  'balance', 'created_at']
        read_only_fields = ['id', 'account_number', 'balance', 'created_at']

    def validate(self, attrs):
        user = self.context['request'].user
        if not check_account_limit(user):
            raise serializers.ValidationError(
                "You can have a maximum of 3 bank accounts."
            )
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['account_number'] = generate_account_number()
        return super().create(validated_data)


class TopUpSerializer(serializers.Serializer):
    """Serializer for topping up an account balance."""
    account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Top-up amount must be positive.")
        return value
