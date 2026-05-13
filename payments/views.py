from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import PaymentSerializer, TransactionSerializer
from .services import process_payment


class PaymentView(APIView):
    """
    POST /api/payments/pay/
    Process a payment from the authenticated user's bank account
    to a receiver's bank account.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        txn = process_payment(
            sender=request.user,
            sender_account_id=serializer.validated_data['sender_account_id'],
            receiver_account_number=serializer.validated_data['receiver_account_number'],
            amount=serializer.validated_data['amount'],
            remarks=serializer.validated_data.get('remarks', ''),
        )

        response_data = TransactionSerializer(txn).data

        if txn.status == 'SUCCESS':
            return Response(
                {"message": "Payment successful.", "transaction": response_data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Payment failed.", "transaction": response_data},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TransactionListView(generics.ListAPIView):
    """
    GET /api/payments/transactions/
    List all transactions where the authenticated user is the sender.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Transaction.objects.none()
        return Transaction.objects.filter(sender=self.request.user)
