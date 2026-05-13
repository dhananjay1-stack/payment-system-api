from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/', views.PaymentView.as_view(), name='pay'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
]
