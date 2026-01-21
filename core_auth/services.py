"""
Service layer for authentication operations.

Simple function-based services for authentication, OTP, and email operations.
"""

import logging
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPToken
from .tasks import send_password_reset_otp_email_task, send_email_verification_otp_task

User = get_user_model()
logger = logging.getLogger(__name__)


# =============================================================================
# USER OPERATIONS
# =============================================================================

def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email address."""
    try:
        return User.objects.get(email=email.lower())
    except User.DoesNotExist:
        return None


def create_user(email: str, password: str, **kwargs) -> User:
    """Create a new user."""
    return User.objects.create_user(
        email=email.lower(), password=password, **kwargs
    )


def update_user(user: User, **kwargs) -> User:
    """Update user profile."""
    for field, value in kwargs.items():
        if hasattr(user, field):
            setattr(user, field, value)
    user.save()
    return user


# =============================================================================
# AUTHENTICATION
# =============================================================================

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    return authenticate(email=email.lower(), password=password)


# =============================================================================
# JWT TOKENS
# =============================================================================

def get_tokens_for_user(user: User) -> dict:
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def blacklist_token(refresh_token: str) -> bool:
    """Blacklist a refresh token (logout)."""
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True
    except Exception as e:
        logger.error("Failed to blacklist refresh token", exc_info=e)
        return False


# =============================================================================
# OTP OPERATIONS
# =============================================================================

def generate_otp(user: User, purpose: str) -> OTPToken:
    """Generate an OTP for the specified user and purpose."""
    return OTPToken.create_otp(user, purpose)


def verify_otp(
    user: User,
    otp: str,
    purpose: str,
    validate_only: bool = False
) -> bool:
    """Verify an OTP for the user."""
    try:
        otp_token = OTPToken.objects.get(
            user=user,
            token=otp,
            purpose=purpose,
            is_used=False,
        )

        if not otp_token.is_valid:
            return False

        if not validate_only:
            otp_token.mark_as_used()

        return True

    except OTPToken.DoesNotExist:
        return False


# =============================================================================
# PASSWORD OPERATIONS
# =============================================================================

def change_password(user: User, new_password: str) -> bool:
    """Change user's password."""
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True


def request_password_reset_otp(email: str) -> bool:
    """
    Step 1 of forgot password flow.
    Returns True if email was sent successfully, False otherwise.
    """
    user = get_user_by_email(email)
    if not user:
        return False

    otp_token = generate_otp(user, OTPToken.OTPPurpose.PASSWORD_RESET)
    return send_password_reset_otp_email(user, otp_token.token)


def verify_reset_otp(email: str, otp: str) -> bool:
    """Step 2: Verify and consume the OTP."""
    user = get_user_by_email(email)
    if not user:
        return False

    return verify_otp(
        user,
        otp,
        OTPToken.OTPPurpose.PASSWORD_RESET,
        validate_only=False,
    )


def reset_password(email: str, new_password: str) -> bool:
    """Step 3: Reset password if OTP was recently verified."""
    user = get_user_by_email(email)
    if not user:
        return False

    # Check if there's a recently used OTP (within last 10 minutes)
    recent_time = timezone.now() - timedelta(minutes=10)
    recent_otp = OTPToken.objects.filter(
        user=user,
        purpose=OTPToken.OTPPurpose.PASSWORD_RESET,
        is_used=True,
        created_at__gte=recent_time
    ).exists()

    if recent_otp:
        change_password(user, new_password)
        # Invalidate all password reset OTPs for this user
        OTPToken.objects.filter(
            user=user,
            purpose=OTPToken.OTPPurpose.PASSWORD_RESET
        ).update(is_used=True)
        return True

    return False


# =============================================================================
# EMAIL VERIFICATION
# =============================================================================

def send_verification_email(user: User) -> OTPToken:
    """Send email verification OTP."""
    otp_token = generate_otp(user, OTPToken.OTPPurpose.EMAIL_VERIFICATION)
    send_email_verification_otp(user, otp_token.token)
    return otp_token


def verify_email(user: User, otp: str) -> bool:
    """Verify user's email with OTP."""
    if verify_otp(user, otp, OTPToken.OTPPurpose.EMAIL_VERIFICATION):
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        return True
    return False


# =============================================================================
# EMAIL SENDING
# =============================================================================

def send_password_reset_otp_email(user: User, otp: str) -> bool:
    """Send password reset OTP email asynchronously using Celery."""
    try:
        # Send email asynchronously using Celery task
        send_password_reset_otp_email_task.delay(
            user_email=user.email,
            user_full_name=user.full_name or user.email,
            otp=otp
        )
        logger.info(f"Password reset OTP email task queued for {user.email}")
        return True
    except Exception as e:
        logger.error("Failed to queue password reset OTP email task", exc_info=e)
        return False


def send_email_verification_otp(user: User, otp: str) -> bool:
    """Send email verification OTP asynchronously using Celery."""
    try:
        # Send email asynchronously using Celery task
        send_email_verification_otp_task.delay(
            user_email=user.email,
            user_full_name=user.full_name or user.email,
            otp=otp
        )
        logger.info(f"Email verification OTP task queued for {user.email}")
        return True
    except Exception as e:
        logger.error("Failed to queue email verification OTP task", exc_info=e)
        return False


# =============================================================================
# LEGACY CLASS WRAPPERS (Backward Compatibility)
# =============================================================================

class UserService:
    get_user_by_email = staticmethod(get_user_by_email)
    create_user = staticmethod(create_user)
    update_user = staticmethod(update_user)


class TokenService:
    get_tokens_for_user = staticmethod(get_tokens_for_user)
    blacklist_token = staticmethod(blacklist_token)


class AuthenticationService:
    authenticate_user = staticmethod(authenticate_user)
    logout = staticmethod(blacklist_token)


class PasswordService:
    change_password = staticmethod(change_password)


class PasswordResetService:
    request_password_reset_otp = staticmethod(request_password_reset_otp)
    verify_reset_otp = staticmethod(verify_reset_otp)
    reset_password = staticmethod(reset_password)


class EmailVerificationService:
    send_verification_email = staticmethod(send_verification_email)
    verify_email = staticmethod(verify_email)


class EmailService:
    send_password_reset_otp_email = staticmethod(send_password_reset_otp_email)
    send_email_verification_otp = staticmethod(send_email_verification_otp)


class OTPService:
    generate_otp = staticmethod(generate_otp)
    verify_otp = staticmethod(verify_otp)
