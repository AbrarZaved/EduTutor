"""
Admin configuration for the core_auth app.

This module registers models with the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import OTPToken, PasswordResetToken, User
from django.contrib.auth.models import Group

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for the User model.
    """

    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_email_verified",
        "is_active",
        "is_staff",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "is_email_verified",
        "created_at",
    ]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal Info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    'role',
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_email_verified",
                    "is_active",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for OTP tokens.
    """

    list_display = [
        "user",
        "purpose",
        "is_used",
        "created_at",
        "expires_at",
        "is_valid_display",
    ]
    list_filter = ["purpose", "is_used", "created_at"]
    search_fields = ["user__email", "token"]
    ordering = ["-created_at"]
    readonly_fields = ["token", "created_at"]

    def is_valid_display(self, obj):
        """Display whether the OTP is valid."""
        return obj.is_valid

    is_valid_display.boolean = True
    is_valid_display.short_description = "Valid"


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for password reset tokens.
    """

    list_display = [
        "user",
        "is_used",
        "created_at",
        "expires_at",
        "is_valid_display",
    ]
    list_filter = ["is_used", "created_at"]
    search_fields = ["user__email"]
    ordering = ["-created_at"]
    readonly_fields = ["token", "created_at"]

    def is_valid_display(self, obj):
        """Display whether the token is valid."""
        return obj.is_valid

    is_valid_display.boolean = True
    is_valid_display.short_description = "Valid"
