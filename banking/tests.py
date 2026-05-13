from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import BankAccount

User = get_user_model()


class BankAccountTests(TestCase):
    """Tests for bank account creation, listing, deletion, and top-up."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='bankuser', password='testpass123'
        )
        login = self.client.post(
            '/api/accounts/login/',
            {'username': 'bankuser', 'password': 'testpass123'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )

    def _create_account(self, bank_name='Test Bank'):
        return self.client.post(
            '/api/banking/accounts/',
            {'bank_name': bank_name, 'account_type': 'savings'},
            format='json',
        )

    def test_create_bank_account(self):
        response = self._create_account()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['account']['owner'], 'bankuser')

    def test_max_three_accounts(self):
        """Enforce the 3 bank account limit per user."""
        self._create_account('Bank A')
        self._create_account('Bank B')
        self._create_account('Bank C')
        # 4th should fail
        response = self._create_account('Bank D')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_accounts(self):
        self._create_account()
        response = self.client.get('/api/banking/accounts/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_account(self):
        create_resp = self._create_account()
        account_id = create_resp.data['account']['id']
        response = self.client.delete(f'/api/banking/accounts/{account_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_topup_account(self):
        create_resp = self._create_account()
        account_id = create_resp.data['account']['id']
        response = self.client.post(
            '/api/banking/topup/',
            {'account_id': account_id, 'amount': '500.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(response.data['account']['balance']), '500.00'
        )

    def test_topup_negative_amount(self):
        create_resp = self._create_account()
        account_id = create_resp.data['account']['id']
        response = self.client.post(
            '/api/banking/topup/',
            {'account_id': account_id, 'amount': '-100.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
