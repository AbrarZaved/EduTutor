"""
Serializers for the Profile app.

This module contains serializers for user profile management.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Provides a complete representation of user data,
    excluding sensitive fields like password.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "role",
            "is_email_verified",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_email_verified",
            "is_active",
            "created_at",
            "updated_at",
        ]
    
    def get_full_name(self, obj):
        """Get the user's full name from the property."""
        return obj.full_name


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.

    Only allows updating non-sensitive profile fields.
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "role",
        ]

    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value:
            # Remove spaces and dashes
            cleaned = value.replace(" ", "").replace("-", "")
            if not cleaned.replace("+", "").isdigit():
                raise serializers.ValidationError(
                    "Phone number must contain only digits, spaces, dashes, or a leading plus sign."
                )
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password (when user is logged in).
    """

    current_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """Validate passwords."""
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match."}
            )
        return attrs

    def validate_current_password(self, value):
        """Validate that current password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=4, max_length=10)
