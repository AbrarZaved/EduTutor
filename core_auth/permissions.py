"""
Custom permissions for the core_auth app.

This module defines custom permission classes that respect
the AUTH_FEATURES configuration settings.
"""

from django.conf import settings
from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access for unauthenticated users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsPasswordResetEnabled(permissions.BasePermission):
    """
    Permission class that checks if password reset is enabled.

    Returns True only if ENABLE_PASSWORD_RESET is True in AUTH_FEATURES.
    """

    message = "Password reset functionality is currently disabled."

    def has_permission(self, request, view):
        auth_features = getattr(settings, "AUTH_FEATURES", {})
        return auth_features.get("ENABLE_PASSWORD_RESET", True)


class IsProfileEditEnabled(permissions.BasePermission):
    """
    Permission class that checks if profile editing is enabled.

    Returns True only if ENABLE_PROFILE_EDIT is True in AUTH_FEATURES.
    """

    message = "Profile editing functionality is currently disabled."

    def has_permission(self, request, view):
        auth_features = getattr(settings, "AUTH_FEATURES", {})
        return auth_features.get("ENABLE_PROFILE_EDIT", True)


class IsEmailVerified(permissions.BasePermission):
    """
    Permission class that requires the user's email to be verified.
    """

    message = "Please verify your email address to access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_email_verified
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows access only to the owner of an object or admins.

    Requires the object to have a 'user' attribute or be the user itself.
    """

    def has_object_permission(self, request, view, obj):
        # Allow admins
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check if obj is a User instance
        if hasattr(obj, "email"):
            return obj == request.user

        # Check if obj has a user attribute
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsAdminUser(permissions.BasePermission):
    """
    Permission class that only allows admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsTeacher(permissions.BasePermission):
    """
    Permission class that only allows users with the 'teacher' role.
    """

    message = "You must be a teacher to access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "teacher"
        )
    

class IsStudent(permissions.BasePermission):
    """
    Permission class that only allows users with the 'student' role.
    """

    message = "You must be a student to access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "student"
        )
        

class IsParent(permissions.BasePermission):
    """
    Permission class that only allows users with the 'parent' role.
    """

    message = "You must be a parent to access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "parent"
        )