from django.contrib import admin
from .models import BankAccount


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'bank_name', 'user', 'account_type',
                    'balance', 'is_active', 'created_at')
    list_filter = ('bank_name', 'account_type', 'is_active')
    search_fields = ('account_number', 'user__username', 'bank_name')
    readonly_fields = ('id', 'account_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)
