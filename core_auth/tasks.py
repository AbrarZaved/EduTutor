"""
Celery tasks for email operations.

All email sending operations are handled asynchronously through Celery.
"""

import logging
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_otp_email_task(self, user_email: str, user_full_name: str, otp: str):
    """
    Send password reset OTP email asynchronously.
    
    Args:
        user_email: Recipient email address
        user_full_name: User's full name or fallback to email
        otp: One-time password code
    """
    subject = "Password Reset OTP"
    message = f"""Hello {user_full_name or user_email},

Your OTP code is: {otp}

This code will expire in {settings.AUTH_FEATURES.get('OTP_EXPIRY_MINUTES', 10)} minutes.

If you did not request this, please ignore this email.
"""

    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f"Password reset OTP email sent successfully to {user_email}")
        return result > 0
    except Exception as exc:
        logger.error(f"Failed to send password reset OTP email to {user_email}: {str(exc)}")
        # Retry the task if it fails
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_verification_otp_task(self, user_email: str, user_full_name: str, otp: str):
    """
    Send email verification OTP asynchronously.
    
    Args:
        user_email: Recipient email address
        user_full_name: User's full name or fallback to email
        otp: One-time password code
    """
    subject = "Verify Your Email Address"
    message = f"""Hello {user_full_name or user_email},

Your verification OTP is: {otp}

This code will expire in {settings.AUTH_FEATURES.get('OTP_EXPIRY_MINUTES', 10)} minutes.
"""

    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f"Email verification OTP sent successfully to {user_email}")
        return result > 0
    except Exception as exc:
        logger.error(f"Failed to send email verification OTP to {user_email}: {str(exc)}")
        # Retry the task if it fails
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_generic_email_task(
    self,
    subject: str,
    message: str,
    recipient_list: list,
    from_email: str = None,
    html_message: str = None
):
    """
    Send a generic email asynchronously.
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_list: List of recipient email addresses
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
        html_message: Optional HTML version of the message
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f"Generic email sent successfully to {recipient_list}")
        return result > 0
    except Exception as exc:
        logger.error(f"Failed to send generic email to {recipient_list}: {str(exc)}")
        # Retry the task if it fails
        raise self.retry(exc=exc)
