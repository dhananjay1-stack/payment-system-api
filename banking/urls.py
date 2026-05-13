from django.urls import path
from . import views

app_name = 'banking'

urlpatterns = [
    path('accounts/', views.BankAccountCreateView.as_view(), name='account-create'),
    path('accounts/list/', views.BankAccountListView.as_view(), name='account-list'),
    path('accounts/<uuid:pk>/', views.BankAccountDeleteView.as_view(), name='account-delete'),
    path('topup/', views.TopUpView.as_view(), name='topup'),
]
