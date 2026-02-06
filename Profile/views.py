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
    AdminProfileSerializer,
    AdminProfileUpdateSerializer,
    AdminProfileCreateSerializer,
)
from .models import AdminProfile

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


# ============================================================================
# AdminProfile Views
# ============================================================================


class AdminProfileListView(generics.ListAPIView):
    """
    API view for listing all admin profiles.

    Endpoint: GET /api/profile/admins/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminProfileSerializer
    queryset = AdminProfile.objects.all().select_related('user')

    @extend_schema(
        summary="List all admin profiles",
        description="Retrieve a list of all admin profiles. Requires authentication.",
        responses={
            200: AdminProfileSerializer(many=True),
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminProfileDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving a specific admin profile.

    Endpoint: GET /api/profile/admins/<admin_id>/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminProfileSerializer
    queryset = AdminProfile.objects.all().select_related('user')
    lookup_field = 'admin_id'

    @extend_schema(
        summary="Get admin profile details",
        description="Retrieve detailed information about a specific admin profile by admin_id.",
        responses={
            200: AdminProfileSerializer,
            404: "Not Found - Admin profile does not exist",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminProfileCreateView(generics.CreateAPIView):
    """
    API view for creating a new admin profile.

    Endpoint: POST /api/profile/admins/create/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminProfileCreateSerializer

    @extend_schema(
        summary="Create admin profile",
        description="Create a new admin profile for an existing user with 'school_admin' role.",
        request=AdminProfileCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Admin profile created successfully",
                response=AdminProfileSerializer,
            ),
            400: "Bad Request - Invalid input data or profile already exists",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_profile = serializer.save()
        
        return Response(
            {
                "message": "Admin profile created successfully.",
                "admin_profile": AdminProfileSerializer(admin_profile).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminProfileUpdateView(generics.UpdateAPIView):
    """
    API view for updating an admin profile.

    Endpoint: PUT/PATCH /api/profile/admins/<admin_id>/update/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminProfileUpdateSerializer
    queryset = AdminProfile.objects.all()
    lookup_field = 'admin_id'

    @extend_schema(
        summary="Update admin profile",
        description="Update admin profile information. Supports full update with PUT and partial update with PATCH.",
        request=AdminProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Admin profile updated successfully",
                response=AdminProfileSerializer,
            ),
            400: "Bad Request - Invalid input data",
            404: "Not Found - Admin profile does not exist",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "message": "Admin profile updated successfully.",
                "admin_profile": AdminProfileSerializer(instance).data,
            }
        )

    @extend_schema(
        summary="Partially update admin profile",
        description="Partially update admin profile information using PATCH method.",
        request=AdminProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Admin profile updated successfully",
                response=AdminProfileSerializer,
            ),
            400: "Bad Request - Invalid input data",
            404: "Not Found - Admin profile does not exist",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class AdminProfileDeleteView(generics.DestroyAPIView):
    """
    API view for deleting an admin profile.

    Endpoint: DELETE /api/profile/admins/<admin_id>/delete/
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = AdminProfile.objects.all()
    lookup_field = 'admin_id'

    @extend_schema(
        summary="Delete admin profile",
        description="Delete a specific admin profile. This does not delete the associated user.",
        responses={
            204: "No Content - Admin profile deleted successfully",
            404: "Not Found - Admin profile does not exist",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class CurrentAdminProfileView(generics.RetrieveAPIView):
    """
    API view for retrieving the current user's admin profile.

    Endpoint: GET /api/profile/admin/me/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminProfileSerializer

    @extend_schema(
        summary="Get current user's admin profile",
        description="Retrieve the authenticated user's admin profile if they have one.",
        responses={
            200: AdminProfileSerializer,
            404: "Not Found - Current user does not have an admin profile",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        """Get the admin profile for the current authenticated user."""
        try:
            return AdminProfile.objects.select_related('user').get(user=self.request.user)
        except AdminProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Admin profile not found for current user.")


class CurrentAdminProfileUpdateView(generics.UpdateAPIView):
    """
    API view for updating the current user's admin profile.

    Endpoint: PUT/PATCH /api/profile/admin/me/update/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminProfileUpdateSerializer

    @extend_schema(
        summary="Update current user's admin profile",
        description="Update the authenticated user's admin profile. Supports partial updates with PATCH.",
        request=AdminProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Admin profile updated successfully",
                response=AdminProfileSerializer,
            ),
            400: "Bad Request - Invalid input data",
            404: "Not Found - Current user does not have an admin profile",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "message": "Admin profile updated successfully.",
                "admin_profile": AdminProfileSerializer(instance).data,
            }
        )

    @extend_schema(
        summary="Partially update current user's admin profile",
        description="Partially update the authenticated user's admin profile.",
        request=AdminProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Admin profile updated successfully",
                response=AdminProfileSerializer,
            ),
            400: "Bad Request - Invalid input data",
            404: "Not Found - Current user does not have an admin profile",
            401: "Unauthorized - Authentication required"
        },
        tags=['AdminProfile']
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def get_object(self):
        """Get the admin profile for the current authenticated user."""
        try:
            return AdminProfile.objects.get(user=self.request.user)
        except AdminProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Admin profile not found for current user.")

