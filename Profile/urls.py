"""
URL configuration for the Profile app.

This module defines all URL patterns for profile endpoints.
"""

from django.urls import path
from .views import (
    EmailVerificationConfirmView,
    PasswordChangeView,
    ProfileDeleteView,
    ProfileView,
    ProfileUpdateView,
)

app_name = "Profile"

urlpatterns = [
    # Profile View & Update
    path("", ProfileView.as_view(), name="profile"),
    path("update/", ProfileUpdateView.as_view(), name="profile_update"),
    path('delete/', ProfileDeleteView.as_view(), name='profile_delete'),
    # Password Change (authenticated user, knows current password)
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    # Email Verification
    path(
        "email/verify/confirm/",
        EmailVerificationConfirmView.as_view(),
        name="email_verify_confirm",
    ),
]
