from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BankAccount
from .serializers import (
    BankAccountSerializer,
    BankAccountCreateSerializer,
    TopUpSerializer,
)
from .services import top_up_account


class BankAccountCreateView(generics.CreateAPIView):
    """
    POST /api/banking/accounts/
    Create a new bank account for the authenticated user.
    Enforces the 3-account limit via the serializer.
    """
    serializer_class = BankAccountCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        return Response(
            {
                "message": "Bank account created successfully.",
                "account": BankAccountSerializer(account).data,
            },
            status=status.HTTP_201_CREATED,
        )


class BankAccountListView(generics.ListAPIView):
    """
    GET /api/banking/accounts/
    List all active bank accounts of the authenticated user.
    """
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BankAccount.objects.none()
        return BankAccount.objects.filter(
            user=self.request.user, is_active=True
        )


class BankAccountDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/banking/accounts/<id>/
    Soft-delete a bank account (set is_active=False).
    Only the owner can delete their account.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BankAccount.objects.none()
        return BankAccount.objects.filter(
            user=self.request.user, is_active=True
        )

    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        account.is_active = False
        account.save()
        return Response(
            {"message": "Bank account deleted successfully."},
            status=status.HTTP_200_OK,
        )


class TopUpView(APIView):
    """
    POST /api/banking/topup/
    Top up the balance of a bank account owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_id = serializer.validated_data['account_id']
        amount = serializer.validated_data['amount']

        try:
            account = BankAccount.objects.get(
                pk=account_id, user=request.user, is_active=True
            )
        except BankAccount.DoesNotExist:
            return Response(
                {"error": "Bank account not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND,
            )

        account = top_up_account(account, amount)

        return Response(
            {
                "message": "Account topped up successfully.",
                "account": BankAccountSerializer(account).data,
            },
            status=status.HTTP_200_OK,
        )
