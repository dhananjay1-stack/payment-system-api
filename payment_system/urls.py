"""
Root URL configuration for payment_system.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger / ReDoc schema
schema_view = get_schema_view(
    openapi.Info(
        title="Payment System API",
        default_version='v1',
        description="A secure mini payment system with JWT authentication, "
                    "bank account management, and transaction processing.",
        contact=openapi.Contact(email="student@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Root redirect to API docs
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),

    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/banking/', include('banking.urls')),
    path('api/payments/', include('payments.urls')),

    # Swagger docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
