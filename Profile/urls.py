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
    AdminProfileListView,
    AdminProfileDetailView,
    AdminProfileCreateView,
    AdminProfileUpdateView,
    AdminProfileDeleteView,
    CurrentAdminProfileView,
    CurrentAdminProfileUpdateView,
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
    
    # AdminProfile Endpoints
    path("admins/", AdminProfileListView.as_view(), name="admin_profile_list"),
    path("admins/create/", AdminProfileCreateView.as_view(), name="admin_profile_create"),
    path("admins/<str:admin_id>/", AdminProfileDetailView.as_view(), name="admin_profile_detail"),
    path("admins/<str:admin_id>/update/", AdminProfileUpdateView.as_view(), name="admin_profile_update"),
    path("admins/<str:admin_id>/delete/", AdminProfileDeleteView.as_view(), name="admin_profile_delete"),
    
    # Current User's Admin Profile
    path("admin/me/", CurrentAdminProfileView.as_view(), name="current_admin_profile"),
    path("admin/me/update/", CurrentAdminProfileUpdateView.as_view(), name="current_admin_profile_update"),
]
