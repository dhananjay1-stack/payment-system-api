from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth endpoints
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User CRUD endpoints
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('update/', views.UserUpdateView.as_view(), name='update'),
    path('delete/', views.UserDeleteView.as_view(), name='delete'),
    path('users/', views.UserListView.as_view(), name='user-list'),
]
