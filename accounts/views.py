from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, UserUpdateSerializer, UserProfileSerializer

User = get_user_model()


class UserCreateView(generics.CreateAPIView):
    """
    POST /api/accounts/register/
    Register a new user. Open endpoint (no auth required).
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveAPIView):
    """
    GET /api/accounts/profile/
    Returns the authenticated user's own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /api/accounts/update/
    Update the authenticated user's profile.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Profile updated successfully.",
                "user": UserProfileSerializer(user).data,
            }
        )


class UserDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/accounts/delete/
    Soft-deletes the authenticated user by deactivating the account.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(
            {"message": "Account deactivated successfully."},
            status=status.HTTP_200_OK,
        )


class UserListView(generics.ListAPIView):
    """
    GET /api/accounts/users/
    Admin-only endpoint to list all users.
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
