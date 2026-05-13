from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """Handles user registration with password hashing."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name',
                  'last_name', 'phone', 'date_of_birth']
        read_only_fields = ['id']

    def create(self, validated_data):
        # Use create_user so password gets hashed properly
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone'),
            date_of_birth=validated_data.get('date_of_birth'),
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Handles updating user profile fields (not password)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth']


class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only serializer for viewing user profiles."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone', 'date_of_birth', 'date_joined']
        read_only_fields = fields
