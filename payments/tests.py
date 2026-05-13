from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from banking.models import BankAccount
from .models import Transaction

User = get_user_model()


class PaymentTests(TestCase):
    """Tests for payment processing and transaction listing."""

    def setUp(self):
        self.client_a = APIClient()
        self.client_b = APIClient()

        # Create two users
        self.user_a = User.objects.create_user(
            username='sender', password='testpass123'
        )
        self.user_b = User.objects.create_user(
            username='receiver', password='testpass123'
        )

        # Log in user A
        login_a = self.client_a.post(
            '/api/accounts/login/',
            {'username': 'sender', 'password': 'testpass123'},
            format='json',
        )
        self.client_a.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_a.data['access']}"
        )

        # Log in user B
        login_b = self.client_b.post(
            '/api/accounts/login/',
            {'username': 'receiver', 'password': 'testpass123'},
            format='json',
        )
        self.client_b.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_b.data['access']}"
        )

        # Create bank accounts
        resp_a = self.client_a.post(
            '/api/banking/accounts/',
            {'bank_name': 'Sender Bank', 'account_type': 'savings'},
            format='json',
        )
        self.sender_account_id = resp_a.data['account']['id']
        self.sender_account_number = resp_a.data['account']['account_number']

        resp_b = self.client_b.post(
            '/api/banking/accounts/',
            {'bank_name': 'Receiver Bank', 'account_type': 'savings'},
            format='json',
        )
        self.receiver_account_number = resp_b.data['account']['account_number']

        # Top up sender's account with 1000
        self.client_a.post(
            '/api/banking/topup/',
            {'account_id': self.sender_account_id, 'amount': '1000.00'},
            format='json',
        )

    def test_successful_payment(self):
        response = self.client_a.post(
            '/api/payments/pay/',
            {
                'sender_account_id': self.sender_account_id,
                'receiver_account_number': self.receiver_account_number,
                'amount': '200.00',
                'remarks': 'Test payment',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction']['status'], 'SUCCESS')

        # Verify balances
        sender_acc = BankAccount.objects.get(pk=self.sender_account_id)
        receiver_acc = BankAccount.objects.get(
            account_number=self.receiver_account_number
        )
        self.assertEqual(sender_acc.balance, Decimal('800.00'))
        self.assertEqual(receiver_acc.balance, Decimal('200.00'))

    def test_insufficient_balance(self):
        response = self.client_a.post(
            '/api/payments/pay/',
            {
                'sender_account_id': self.sender_account_id,
                'receiver_account_number': self.receiver_account_number,
                'amount': '5000.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['transaction']['status'], 'FAILED')

    def test_invalid_receiver_account(self):
        response = self.client_a.post(
            '/api/payments/pay/',
            {
                'sender_account_id': self.sender_account_id,
                'receiver_account_number': '000000000000',
                'amount': '100.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['transaction']['status'], 'FAILED')

    def test_self_transfer(self):
        response = self.client_a.post(
            '/api/payments/pay/',
            {
                'sender_account_id': self.sender_account_id,
                'receiver_account_number': self.sender_account_number,
                'amount': '100.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_list(self):
        # Make a payment first
        self.client_a.post(
            '/api/payments/pay/',
            {
                'sender_account_id': self.sender_account_id,
                'receiver_account_number': self.receiver_account_number,
                'amount': '50.00',
            },
            format='json',
        )
        response = self.client_a.get('/api/payments/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_negative_payment_amount(self):
        response = self.client_a.post(
            '/api/payments/pay/',
            {
                'sender_account_id': self.sender_account_id,
                'receiver_account_number': self.receiver_account_number,
                'amount': '-50.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
