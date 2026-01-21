"""
Tests for authentication services.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core_auth.models import OTPToken
from core_auth.services import (
    AuthenticationService,
    OTPService,
    PasswordResetService,
    PasswordService,
    TokenService,
    UserService,
)

User = get_user_model()


class UserServiceTestCase(TestCase):
    """Test cases for UserService."""

    def test_get_user_by_email(self):
        """Test getting user by email."""
        user = User.objects.create_user(
            email="testuser@example.com", password="SecurePass123!"
        )
        found_user = UserService.get_user_by_email("testuser@example.com")
        self.assertEqual(found_user, user)

    def test_get_user_by_email_not_found(self):
        """Test getting non-existent user."""
        found_user = UserService.get_user_by_email("nonexistent@example.com")
        self.assertIsNone(found_user)

    def test_create_user(self):
        """Test creating user via service."""
        user = UserService.create_user(
            email="newuser@example.com",
            password="SecurePass123!",
            first_name="New",
            last_name="User",
        )
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.first_name, "New")


class TokenServiceTestCase(TestCase):
    """Test cases for TokenService."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="SecurePass123!"
        )

    def test_get_tokens_for_user(self):
        """Test generating tokens for user."""
        tokens = TokenService.get_tokens_for_user(self.user)
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)
        self.assertIsNotNone(tokens["access"])
        self.assertIsNotNone(tokens["refresh"])


class AuthenticationServiceTestCase(TestCase):
    """Test cases for AuthenticationService."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="SecurePass123!"
        )

    def test_authenticate_user_success(self):
        """Test successful authentication."""
        user = AuthenticationService.authenticate_user(
            email="testuser@example.com", password="SecurePass123!"
        )
        self.assertEqual(user, self.user)

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        user = AuthenticationService.authenticate_user(
            email="testuser@example.com", password="WrongPassword!"
        )
        self.assertIsNone(user)

    def test_login_success(self):
        """Test successful login."""
        user, tokens = AuthenticationService.login(
            email="testuser@example.com", password="SecurePass123!"
        )
        self.assertEqual(user, self.user)
        self.assertIsNotNone(tokens)


class OTPServiceTestCase(TestCase):
    """Test cases for OTPService."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="SecurePass123!"
        )

    def test_generate_otp(self):
        """Test OTP generation."""
        otp_token = OTPService.generate_otp(
            self.user, OTPToken.OTPPurpose.PASSWORD_RESET
        )
        self.assertIsNotNone(otp_token)
        self.assertEqual(otp_token.user, self.user)
        self.assertEqual(otp_token.purpose, OTPToken.OTPPurpose.PASSWORD_RESET)

    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        otp_token = OTPService.generate_otp(
            self.user, OTPToken.OTPPurpose.PASSWORD_RESET
        )
        result = OTPService.verify_otp(
            self.user, otp_token.token, OTPToken.OTPPurpose.PASSWORD_RESET
        )
        self.assertTrue(result)

    def test_verify_otp_invalid(self):
        """Test invalid OTP verification."""
        result = OTPService.verify_otp(
            self.user, "000000", OTPToken.OTPPurpose.PASSWORD_RESET
        )
        self.assertFalse(result)


class PasswordServiceTestCase(TestCase):
    """Test cases for PasswordService."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="OldPassword123!"
        )

    def test_change_password(self):
        """Test password change."""
        result = PasswordService.change_password(self.user, "NewPassword123!")
        self.assertTrue(result)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))
