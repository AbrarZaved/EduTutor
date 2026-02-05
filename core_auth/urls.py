"""
URL configuration for the core_auth app.

This module defines all URL patterns for authentication endpoints.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    ForgotPasswordRequestView,
    ForgotPasswordVerifyOTPView,
    ForgotPasswordResetView,
    LoginView,
    LogoutView,
    RegisterView,
    TokenRefreshAPIView,
)

app_name = "core_auth"

urlpatterns = [
    # =========================================================================
    # AUTHENTICATION ENDPOINTS
    # =========================================================================
    # User Registration
    path("register/", RegisterView.as_view(), name="register"),
    # Login / Logout
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # JWT Token Management
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    # =========================================================================
    # FORGOT PASSWORD ENDPOINTS (3-step process)
    # =========================================================================
    # Step 1: Request OTP (email only)
    path(
        "forgot-password/request/",
        ForgotPasswordRequestView.as_view(),
        name="forgot_password_request",
    ),
    # Step 2: Verify OTP (email + OTP)
    path(
        "forgot-password/verify-otp/",
        ForgotPasswordVerifyOTPView.as_view(),
        name="forgot_password_verify_otp",
    ),
    # Step 3: Reset password (email + OTP + new password)
    path(
        "forgot-password/reset/",
        ForgotPasswordResetView.as_view(),
        name="forgot_password_reset",
    ),
]
