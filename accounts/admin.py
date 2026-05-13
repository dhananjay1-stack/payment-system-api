from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for our User model with extra fields."""
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'phone', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)

    # Add our custom fields to the admin form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('phone', 'date_of_birth')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile Info', {'fields': ('phone', 'date_of_birth')}),
    )
