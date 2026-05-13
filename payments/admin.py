from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'sender', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reference_id', 'sender__username')
    readonly_fields = (
        'id', 'reference_id', 'sender', 'sender_account',
        'receiver_account', 'amount', 'status', 'remarks',
        'failure_reason', 'sender_balance_before', 'sender_balance_after',
        'receiver_balance_before', 'receiver_balance_after', 'created_at',
    )
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        # Transactions should only be created via the API
        return False

    def has_change_permission(self, request, obj=None):
        return False
