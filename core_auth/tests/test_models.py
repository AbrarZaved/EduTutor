"""
Tests for User model.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test cases for the User model."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email="testuser@example.com", password="SecurePass123!"
        )
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("SecurePass123!"))

    def test_create_user_without_email(self):
        """Test that creating user without email raises error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="SecurePass123!")

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            email="admin@example.com", password="AdminPass123!"
        )
        self.assertEqual(admin.email, "admin@example.com")
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_full_name(self):
        """Test the full_name property."""
        user = User.objects.create_user(
            email="testuser@example.com",
            password="SecurePass123!",
            first_name="John",
            last_name="Doe",
        )
        self.assertEqual(user.full_name, "John Doe")

    def test_user_full_name_empty(self):
        """Test full_name when names are not set."""
        user = User.objects.create_user(
            email="testuser@example.com", password="SecurePass123!"
        )
        self.assertEqual(user.full_name, "testuser@example.com")

    def test_email_normalized(self):
        """Test that email is normalized (lowercase)."""
        user = User.objects.create_user(
            email="TestUser@EXAMPLE.COM", password="SecurePass123!"
        )
        self.assertEqual(user.email, "testuser@example.com")
