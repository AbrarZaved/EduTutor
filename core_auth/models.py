"""
Custom User Model and Authentication-related Models.

This module defines the custom User model extending AbstractUser,
as well as OTP models for password reset and profile verification.
"""

import secrets
import string
from datetime import timedelta
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from Profile.models import StudentProfile, TeacherProfile, ParentProfile

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Provides helper methods for creating regular users and superusers.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.

        Args:
            email: User's email address (required).
            password: User's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.

        Args:
            email: Superuser's email address (required).
            password: Superuser's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("parent", "Parent"),
        ("school_admin", "Admin"),
    ]

    username = None
    email = models.EmailField(unique=True, db_index=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    is_email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email
    

@receiver(pre_save, sender=User)
def _capture_email_verified_state(sender, instance, **kwargs):
    """
    Store previous is_email_verified on the instance so post_save can compare.
    """
    if not instance.pk:
        instance._prev_is_email_verified = False
        return

    prev = User.objects.filter(pk=instance.pk).values_list("is_email_verified", flat=True).first()
    instance._prev_is_email_verified = bool(prev)


@receiver(post_save, sender=User)
def create_profile_when_email_verified(sender, instance, created, **kwargs):
    """
    Create role profile only when email becomes verified (False -> True).
    """
    if not instance.is_email_verified:
        return

    # create ONLY when it just turned True, or when user is created already verified
    just_verified = created or (getattr(instance, "_prev_is_email_verified", False) is False)

    if not just_verified:
        return

    profile_model_map = {
        "student": StudentProfile,
        "teacher": TeacherProfile,
        "parent": ParentProfile,
    }

    profile_model = profile_model_map.get(instance.role)
    if not profile_model:
        return

    profile_model.objects.get_or_create(user=instance)

class OTPToken(models.Model):
    """
    Model to store OTP tokens for various verification purposes.

    Used for:
    - Password reset verification
    - Email verification
    - Profile change verification (e.g., change password)
    """

    class OTPPurpose(models.TextChoices):
        PASSWORD_RESET = "password_reset", "Password Reset"
        EMAIL_VERIFICATION = "email_verification", "Email Verification"
        CHANGE_PASSWORD = "change_password", "Change Password"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_tokens")
    token = models.CharField(max_length=10, db_index=True)
    purpose = models.CharField(max_length=20, choices=OTPPurpose.choices)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "OTP Token"
        verbose_name_plural = "OTP Tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token", "purpose"]),
            models.Index(fields=["user", "purpose", "is_used"]),
        ]

    def __str__(self):
        return f"OTP for {self.user.email} - {self.purpose}"

    @property
    def is_expired(self):
        """Check if the OTP token has expired."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if the OTP token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark the OTP token as used."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    @classmethod
    def generate_otp(cls, length=None):
        """
        Generate a random OTP code.

        Args:
            length: Length of the OTP. Defaults to settings value.

        Returns:
            str: The generated OTP code.
        """
        if length is None:
            length = getattr(settings, "AUTH_FEATURES", {}).get("OTP_LENGTH", 4)

        return "".join(secrets.choice(string.digits) for _ in range(length))

    @classmethod
    def create_otp(cls, user, purpose):
        """
        Create a new OTP token for the specified user and purpose.

        Invalidates any existing unused tokens for the same purpose.

        Args:
            user: The user to create OTP for.
            purpose: The purpose of the OTP (from OTPPurpose choices).

        Returns:
            OTPToken: The created OTP token instance.
        """
        # Invalidate existing unused tokens for the same purpose
        cls.objects.filter(user=user, purpose=purpose, is_used=False).update(
            is_used=True
        )

        # Get expiry time from settings
        expiry_minutes = getattr(settings, "AUTH_FEATURES", {}).get(
            "OTP_EXPIRY_MINUTES", 10
        )

        # Create new OTP token
        otp_token = cls.objects.create(
            user=user,
            token=cls.generate_otp(),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )

        return otp_token


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens.

    This is an alternative to OTP-based password reset,
    using a longer token sent via email link.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.CharField(max_length=100, unique=True, db_index=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Password reset for {self.user.email}"

    @property
    def is_expired(self):
        """Check if the reset token has expired."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if the reset token is valid."""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark the reset token as used."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    @classmethod
    def generate_token(cls):
        """Generate a secure random token."""
        return secrets.token_urlsafe(64)

    @classmethod
    def create_token(cls, user, expiry_hours=24):
        """
        Create a new password reset token for the user.

        Args:
            user: The user to create token for.
            expiry_hours: Hours until the token expires.

        Returns:
            PasswordResetToken: The created token instance.
        """
        # Invalidate existing tokens
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        return cls.objects.create(
            user=user,
            token=cls.generate_token(),
            expires_at=timezone.now() + timedelta(hours=expiry_hours),
        )
