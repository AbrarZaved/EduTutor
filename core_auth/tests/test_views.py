"""
Tests for authentication views.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class RegistrationTestCase(TestCase):
    """Test cases for user registration."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("core_auth:register")

    def test_registration_success(self):
        """Test successful user registration."""
        data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("user", response.data)

    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "confirm_password": "DifferentPass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        User.objects.create_user(
            email="existing@example.com", password="ExistingPass123!"
        )
        data = {
            "email": "existing@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTestCase(TestCase):
    """Test cases for user login."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("core_auth:login")
        self.user = User.objects.create_user(
            email="testuser@example.com", password="SecurePass123!"
        )

    def test_login_success(self):
        """Test successful login."""
        data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            "email": "testuser@example.com",
            "password": "WrongPassword!",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTestCase(TestCase):
    """Test cases for profile operations."""

    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse("core_auth:profile")
        self.profile_update_url = reverse("core_auth:profile_update")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test retrieving user profile."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_update_profile(self):
        """Test updating user profile."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio",
        }
        response = self.client.patch(self.profile_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.bio, "Updated bio")


class PasswordChangeTestCase(TestCase):
    """Test cases for password change."""

    def setUp(self):
        self.client = APIClient()
        self.password_change_url = reverse("core_auth:password_change")
        self.user = User.objects.create_user(
            email="testuser@example.com", password="OldPassword123!"
        )
        self.client.force_authenticate(user=self.user)

    def test_password_change_success(self):
        """Test successful password change."""
        data = {
            "current_password": "OldPassword123!",
            "new_password": "NewSecurePass123!",
            "new_confirm_password": "NewSecurePass123!",
        }
        response = self.client.post(self.password_change_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePass123!"))

    def test_password_change_wrong_current(self):
        """Test password change with wrong current password."""
        data = {
            "current_password": "WrongPassword!",
            "new_password": "NewSecurePass123!",
            "new_confirm_password": "NewSecurePass123!",
        }
        response = self.client.post(self.password_change_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
