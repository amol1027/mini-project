"""
Email utilities for user registration and verification
"""
import re
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import EmailVerificationToken
import logging

logger = logging.getLogger(__name__)


def validate_email_address(email):
    """
    Validate email address format and check for common issues
    
    Args:
        email: Email address to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not email:
        return False, "Email address is required"
    
    # Check email format
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email):
        return False, "Invalid email format"
    
    # Check length constraints (RFC 5321)
    if len(email) > 254:
        return False, "Email address too long"
    
    local_part, domain = email.rsplit('@', 1)
    if len(local_part) > 64:
        return False, "Email local part too long"
    
    return True, None


def send_verification_email(user, request):
    """
    Send email verification link to the user
    
    Args:
        user: User instance
        request: HTTP request object to build absolute URIs
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Validate email address
        is_valid, error_msg = validate_email_address(user.email)
        if not is_valid:
            logger.error(f"Invalid email address for user {user.id}: {error_msg}")
            return False
        
        # Check for recent verification emails (rate limiting)
        recent_tokens = EmailVerificationToken.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).count()
        
        if recent_tokens >= 3:
            logger.warning(f"Rate limit exceeded for user {user.id}")
            return False
        
        # Create verification token
        token_obj = EmailVerificationToken.create_token(user)
        
        # Build verification URL
        verification_path = reverse('registration:verify_email', kwargs={'token': token_obj.token})
        verification_url = request.build_absolute_uri(verification_path)
        
        # Email subject with emoji for better engagement
        subject = '✉️ Verify Your Email - Student Resource Exchange'
        
        # Render HTML email template
        html_message = render_to_string('registration/emails/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
            'expiry_days': settings.EMAIL_VERIFICATION_TIMEOUT_DAYS,
            'current_year': timezone.now().year,
        })
        
        # Plain text version (fallback)
        plain_message = strip_tags(html_message)
        
        # Create email message with proper headers
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=f"Student Resource Exchange <{settings.DEFAULT_FROM_EMAIL}>",
            to=[user.email],
            headers={
                'X-Priority': '1',
                'X-MSMail-Priority': 'High',
                'Importance': 'high',
            }
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)
        
        logger.info(f"Verification email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {str(e)}")
        return False


def delete_expired_tokens():
    """
    Delete expired verification tokens (can be run as a periodic task)
    """
    from django.utils import timezone
    EmailVerificationToken.objects.filter(expires_at__lt=timezone.now()).delete()
