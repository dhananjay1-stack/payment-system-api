import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserRegistrationTests(TestCase):
    """Tests for user registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/accounts/register/'

    def test_register_user_success(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_register_user_missing_password(self):
        data = {'username': 'nopass'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='duplicate', password='pass123456')
        data = {'username': 'duplicate', 'password': 'pass123456'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthTests(TestCase):
    """Tests for login and token refresh."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='authuser', password='testpass123'
        )

    def test_login_success(self):
        response = self.client.post(
            '/api/accounts/login/',
            {'username': 'authuser', 'password': 'testpass123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            '/api/accounts/login/',
            {'username': 'authuser', 'password': 'wrongpassword'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        login = self.client.post(
            '/api/accounts/login/',
            {'username': 'authuser', 'password': 'testpass123'},
            format='json',
        )
        refresh_token = login.data['refresh']
        response = self.client.post(
            '/api/accounts/token/refresh/',
            {'refresh': refresh_token},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class UserProfileTests(TestCase):
    """Tests for profile view and update."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='profileuser',
            password='testpass123',
            email='profile@test.com',
        )
        # Log in and set auth header
        login = self.client.post(
            '/api/accounts/login/',
            {'username': 'profileuser', 'password': 'testpass123'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )

    def test_get_profile(self):
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')

    def test_update_profile(self):
        response = self.client.patch(
            '/api/accounts/update/',
            {'first_name': 'Updated'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], 'Updated')

    def test_profile_unauthenticated(self):
        client = APIClient()  # No auth
        response = client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
