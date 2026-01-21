"""
Serializers for the core_auth app.

This module contains all serializers for user authentication,
registration, profile management, and password operations.
"""

from django.conf import settings
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


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles new user creation with password validation.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "role",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create a new user with the validated data."""
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Used for session-based authentication.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )


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


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.

    Sends OTP or reset link to the user's email.
    """

    email = serializers.EmailField(required=True)
    print(email)
    def validate_email(self, value):
        """Validate that the email exists in the system."""
        # We don't reveal if email exists or not for security
        return value.lower()


class PasswordResetOTPVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying password reset OTP.
    """

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=4, max_length=10)



class PasswordResetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer for setting a new password after OTP verification.
    """

    email = serializers.EmailField(required=True)
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
        """Validate that passwords match."""
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=4, max_length=10)
