"""
Custom token utilities for the core_auth app.

This module provides utilities for JWT token customization and management.
"""

from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    Generate access and refresh tokens for a user.

    Args:
        user: The user instance to generate tokens for.

    Returns:
        dict: Dictionary containing 'refresh' and 'access' tokens.
    """
    refresh = RefreshToken.for_user(user)

    # Add custom claims
    refresh["email"] = user.email
    refresh["full_name"] = user.full_name

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_access_token_for_user(user):
    """
    Generate only an access token for a user.

    Args:
        user: The user instance to generate token for.

    Returns:
        str: The access token string.
    """
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


def blacklist_token(refresh_token):
    """
    Blacklist a refresh token.

    Args:
        refresh_token: The refresh token string to blacklist.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True
    except Exception:
        return False


def verify_token(token):
    """
    Verify if a token is valid.

    Args:
        token: The token string to verify.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        RefreshToken(token)
        return True
    except Exception:
        return False


class CustomRefreshToken(RefreshToken):
    """
    Custom refresh token class with additional claims.
    """

    @classmethod
    def for_user(cls, user):
        """
        Generate a token for the user with custom claims.

        Args:
            user: The user instance.

        Returns:
            CustomRefreshToken: The token instance.
        """
        token = super().for_user(user)

        # Add custom claims
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["is_email_verified"] = user.is_email_verified

        return token
