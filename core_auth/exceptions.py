"""
Custom exception handler for the core_auth app.

This module provides a custom exception handler for DRF
that formats error responses consistently.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.

    Provides consistent error response format across all endpoints.

    Args:
        exc: The exception that was raised.
        context: Additional context about the request.

    Returns:
        Response: The formatted error response.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Handle Django validation errors
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            data = {"errors": exc.message_dict}
        else:
            data = {"errors": {"non_field_errors": list(exc.messages)}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # If response is None, it's an unhandled exception
    if response is None:
        return Response(
            {
                "error": "An unexpected error occurred.",
                "detail": (
                    str(exc)
                    if not isinstance(exc, Exception)
                    else "Internal server error"
                ),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Customize the response format
    if isinstance(exc, exceptions.ValidationError):
        response.data = {"errors": response.data}
    elif isinstance(exc, exceptions.AuthenticationFailed):
        response.data = {
            "error": "Authentication failed",
            "detail": (
                str(exc.detail) if hasattr(exc, "detail") else "Invalid credentials"
            ),
        }
    elif isinstance(exc, exceptions.NotAuthenticated):
        response.data = {
            "error": "Not authenticated",
            "detail": "Authentication credentials were not provided.",
        }
    elif isinstance(exc, exceptions.PermissionDenied):
        response.data = {
            "error": "Permission denied",
            "detail": (
                str(exc.detail)
                if hasattr(exc, "detail")
                else "You do not have permission to perform this action."
            ),
        }
    elif isinstance(exc, Http404):
        response.data = {
            "error": "Not found",
            "detail": "The requested resource was not found.",
        }
    elif isinstance(exc, exceptions.Throttled):
        response.data = {
            "error": "Too many requests",
            "detail": f"Request was throttled. Try again in {exc.wait} seconds.",
            "retry_after": exc.wait,
        }

    return response


class AuthenticationError(Exception):
    """Custom authentication error."""

    pass


class OTPError(Exception):
    """Custom OTP-related error."""

    pass


class PasswordResetError(Exception):
    """Custom password reset error."""

    pass
