"""
Views for the core_auth app.

This module contains all API views for authentication,
user registration, profile management, and password operations.

Views are kept thin by delegating business logic to service classes.
"""

import threading
from .models import OTPToken, User
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .permissions import (
    IsAuthenticatedOrReadOnly,
    IsPasswordResetEnabled,
    IsProfileEditEnabled,
)
from .serializers import (
    EmailVerificationSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetNewPasswordSerializer,
    PasswordResetOTPVerifySerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .services import (
    AuthenticationService,
    EmailVerificationService,
    OTPService,
    PasswordResetService,
    PasswordService,
    TokenService,
    UserService,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.

    Creates a new user account and returns user details with JWT tokens.

    Endpoint: POST /api/auth/register/
    """

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        summary="Register new user",
        description="Register a new user account. Returns user details and JWT tokens upon successful registration.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "message": "Registration successful. Please check your email for verification OTP.",
                        "user": {
                            "id": 1,
                            "email": "",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "student",
                        },
                    }
                }
            ),
            400: "Bad Request - Invalid input data"
        },
        tags=['Authentication']

    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        # Send verification email
        try:
            EmailVerificationService.send_verification_email(user)
            message = "Registration successful. Please check your email for verification OTP."
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send verification email: {e}")
            message = "Registration successful, but we couldn't send the verification email. Please try again later."

        return Response(
            {
                "message": message,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    API view for user login.

    Authenticates user with email and password, returns JWT tokens.

    Endpoint: POST /api/auth/login/
    """

    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Login user",
        description="Authenticate user with email and password. Returns JWT access and refresh tokens.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid credentials",
            401: "Unauthorized - Invalid credentials"
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Authenticate user
        user = AuthenticationService.authenticate_user(
            serializer.validated_data["email"],
            serializer.validated_data["password"],
        )
        
        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        if not user.is_active:
            return Response(
                {"error": "Account is not active."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # Generate tokens
        tokens = TokenService.get_tokens_for_user(user)
        
        return Response(
            {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    API view for user logout.

    Blacklists the refresh token to invalidate the session.

    Endpoint: POST /api/auth/logout/
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Logout user",
        description="Blacklist the refresh token to invalidate the user session.",
        request=dict(
            type="object",
            required=['refresh'],
            properties={
                'refresh': dict(type="string", description='Refresh token to blacklist')
            },
        ),
        responses={
            200: OpenApiResponse(
                description="Logout successful",
                examples={
                    "application/json": {
                        "message": "Successfully logged out."
                    }
                }
            ),
            400: "Bad Request - Invalid or missing refresh token"
        },
        tags=['Authentication']
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            AuthenticationService.logout(refresh_token)

            return Response(
                {"message": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )


class TokenRefreshAPIView(TokenRefreshView):
    """
    API view for refreshing JWT tokens.

    Endpoint: POST /api/auth/token/refresh/
    """

    @extend_schema(
        summary="Refresh JWT token",
        description="Get a new access token using a valid refresh token.",
        responses={
            200: OpenApiResponse(
                description="Token refreshed successfully",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                    }
                }
            ),
            401: "Unauthorized - Invalid refresh token"
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProfileView(generics.RetrieveAPIView):
    """
    API view for retrieving user profile.

    Endpoint: GET /api/auth/profile/
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

    Endpoint: PUT/PATCH /api/auth/profile/update/
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


class PasswordChangeView(APIView):
    """
    API view for changing password (when user knows current password).
    
    For logged-in users who know their current password.

    Endpoint: POST /api/auth/password/change/
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
        tags=['Password Management']
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
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class ForgotPasswordRequestView(APIView):
    """
    API view for requesting forgot password OTP.
    
    Step 1: User provides email, receives OTP.

    Endpoint: POST /api/auth/forgot-password/request/
    """

    permission_classes = [permissions.AllowAny, IsPasswordResetEnabled]

    @extend_schema(
        summary="Request forgot password OTP",
        description="Send OTP to the provided email address for password reset (Step 1: Email only).",
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="OTP sent if email exists",
                examples={
                    "application/json": {
                        "message": "If an account exists with this email, you will receive a password reset OTP."
                    }
                }
            )
        },
        tags=['Forgot Password']
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Send OTP
        try:
            success = PasswordResetService.request_password_reset_otp(
                serializer.validated_data["email"]
            )
            if success:
                return Response(
                    {
                        "message": "Password reset OTP has been sent to your email."
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "error": "Failed to send password reset OTP. Please try again later."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send password reset OTP: {e}")
            return Response(
                {
                    "error": "Failed to send password reset OTP. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ForgotPasswordVerifyOTPView(APIView):
    """
    API view for verifying OTP.
    
    Step 2: User provides email and OTP to verify.

    Endpoint: POST /api/auth/forgot-password/verify-otp/
    """

    permission_classes = [permissions.AllowAny, IsPasswordResetEnabled]

    @extend_schema(
        summary="Verify OTP",
        description="Verify the OTP sent to email (Step 2: Email + OTP). Returns success if OTP is valid.",
        request=PasswordResetOTPVerifySerializer,
        responses={
            200: OpenApiResponse(
                description="OTP verified successfully",
                examples={
                    "application/json": {
                        "message": "OTP verified successfully. You can now reset your password."
                    }
                }
            ),
            400: "Bad Request - Invalid or expired OTP"
        },
        tags=['Forgot Password']
    )
    def post(self, request):
        serializer = PasswordResetOTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify and consume the OTP
        success = PasswordResetService.verify_reset_otp(
            serializer.validated_data["email"],
            serializer.validated_data["otp"]
        )
        
        if success:
            return Response(
                {"message": "OTP verified successfully. You can now reset your password."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Invalid or expired OTP."},
            status=status.HTTP_400_BAD_REQUEST
        )


class ForgotPasswordResetView(APIView):
    """
    API view for resetting password after OTP verification.
    
    Step 3: User provides new password and confirmation.

    Endpoint: POST /api/auth/forgot-password/reset/
    """

    permission_classes = [permissions.AllowAny, IsPasswordResetEnabled]

    @extend_schema(
        summary="Reset password",
        description="Reset password after OTP verification (Step 3: Email + New Password + Confirm Password). Must be called within 10 minutes of OTP verification.",
        request=PasswordResetNewPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset successfully",
                examples={
                    "application/json": {
                        "message": "Password reset successfully. You can now login with your new password."
                    }
                }
            ),
            400: "Bad Request - Invalid data, OTP not verified, or verification expired"
        },
        tags=['Forgot Password']
    )
    def post(self, request):
        serializer = PasswordResetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = PasswordResetService.reset_password(
            serializer.validated_data["email"],
            serializer.validated_data["new_password"],
        )

        if success:
            return Response(
                {"message": "Password reset successfully. You can now login with your new password."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Password reset failed. Please verify your OTP again."},
            status=status.HTTP_400_BAD_REQUEST
        )


class EmailVerificationConfirmView(APIView):
    """
    API view for confirming email verification.

    Endpoint: POST /api/auth/email/verify/confirm/
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
        tags=['Email Verification']
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
