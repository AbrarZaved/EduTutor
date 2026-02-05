"""
Views for the Profile app.

This module contains all API views for user profile management.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core_auth.permissions import IsProfileEditEnabled
from core_auth.services import EmailVerificationService, PasswordService, TokenService
from .serializers import (
    EmailVerificationSerializer,
    PasswordChangeSerializer,
    ProfileUpdateSerializer,
    UserSerializer,
)

User = get_user_model()


class ProfileView(generics.RetrieveAPIView):
    """
    API view for retrieving user profile.

    Endpoint: GET /api/profile/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information.",
        responses={
            200: UserSerializer,
            401: "Unauthorized - Authentication required"
        },
        tags=['Profile']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    """
    API view for updating user profile.

    Endpoint: PUT/PATCH /api/profile/update/
    """

    permission_classes = [permissions.IsAuthenticated, IsProfileEditEnabled]
    serializer_class = ProfileUpdateSerializer

    @extend_schema(
        summary="Update user profile",
        description="Update the authenticated user's profile information. Supports partial updates with PATCH.",
        request=ProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Profile updated successfully",
                examples={
                    "application/json": {
                        "message": "Profile updated successfully.",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required"
        },
        tags=['Profile']
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "message": "Profile updated successfully.",
                "user": UserSerializer(instance).data,
            }
        )

    @extend_schema(
        summary="Partially update user profile",
        description="Partially update the authenticated user's profile information.",
        request=ProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Profile updated successfully",
                examples={
                    "application/json": {
                        "message": "Profile updated successfully.",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required"
        },
        tags=['Profile']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class ProfileDeleteView(generics.DestroyAPIView):
    """
    API view for deleting user profile.

    Endpoint: DELETE /api/profile/delete/
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Delete user profile",
        description="Delete the authenticated user's profile.",
        responses={
            204: "No Content - Profile deleted successfully",
            401: "Unauthorized - Authentication required"
        },
        tags=['Profile']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class PasswordChangeView(APIView):
    """
    API view for changing password (when user knows current password).
    
    For logged-in users who know their current password.

    Endpoint: POST /api/profile/password/change/
    """

    permission_classes = [permissions.IsAuthenticated, IsProfileEditEnabled]

    @extend_schema(
        summary="Change password",
        description="Change password for authenticated user. Requires current password, new password, and confirmation.",
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(
                description="Password changed successfully",
                examples={
                    "application/json": {
                        "message": "Password changed successfully."
                    }
                }
            ),
            400: "Bad Request - Invalid current password or passwords don't match",
            401: "Unauthorized - Authentication required"
        },
        tags=['Profile']
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        PasswordService.change_password(
            request.user, serializer.validated_data["new_password"]
        )

        return Response(
            {"message": "Password changed successfully."}, status=200
        )


class EmailVerificationConfirmView(APIView):
    """
    API view for confirming email verification.

    Endpoint: POST /api/profile/email/verify/confirm/
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Verify email with OTP",
        description="Verify user's email address using OTP sent to email. Returns JWT tokens upon successful verification.",
        request=EmailVerificationSerializer,
        responses={
            200: OpenApiResponse(
                description="Email verified successfully",
                examples={
                    "application/json": {
                        "message": "Email verified successfully.",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "is_email_verified": True
                        },
                        "tokens": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid or expired OTP"
        },
        tags=['Profile']
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get user by email
        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Verify the OTP
        success = EmailVerificationService.verify_email(
            user, serializer.validated_data["otp"]
        )

        if success:
            # Generate tokens for the verified user
            tokens = TokenService.get_tokens_for_user(user)
            
            return Response(
                {
                    "message": "Email verified successfully.",
                    "user": UserSerializer(user).data,
                    "tokens": tokens,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST
        )
