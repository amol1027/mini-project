"""
Email Testing Utility for Student Resource Exchange

This script helps you test the email verification functionality.
"""

import os
import sys
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.test import RequestFactory
from registration.models import User
from registration.email_utils import send_verification_email, validate_email_address


def test_email_validation():
    """Test email validation function"""
    print("\n" + "="*60)
    print("TESTING EMAIL VALIDATION")
    print("="*60)
    
    test_cases = [
        ("test@example.com", True),
        ("user.name+tag@example.co.uk", True),
        ("invalid.email@", False),
        ("@example.com", False),
        ("test@tempmail.com", True),  # Will be blocked by form validation
        ("a" * 65 + "@example.com", False),  # Local part too long
        ("test@example.com", True),
    ]
    
    for email, expected_valid in test_cases:
        is_valid, error = validate_email_address(email)
        status = "✓" if is_valid == expected_valid else "✗"
        print(f"{status} {email:40} -> {'Valid' if is_valid else f'Invalid: {error}'}")


def test_email_template():
    """Test rendering the email template"""
    print("\n" + "="*60)
    print("TESTING EMAIL TEMPLATE RENDERING")
    print("="*60)
    
    try:
        from django.utils import timezone
        
        # Create a mock context
        context = {
            'user': type('User', (), {
                'name': 'John Doe',
                'email': 'john.doe@example.com'
            })(),
            'verification_url': 'http://localhost:8000/register/verify-email/abc123xyz789',
            'expiry_days': 7,
            'current_year': timezone.now().year,
        }
        
        html_content = render_to_string('registration/emails/verification_email.html', context)
        print("✓ Email template rendered successfully")
        print(f"  - Template length: {len(html_content)} characters")
        print(f"  - Contains verification URL: {'verification_url' in html_content or 'verify-email' in html_content}")
        print(f"  - Contains user name: {'John Doe' in html_content}")
        
        # Save to file for preview
        output_path = os.path.join(project_root, 'email_preview.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  - Preview saved to: {output_path}")
        print(f"  - Open in browser to see the design!")
        
    except Exception as e:
        print(f"✗ Error rendering template: {e}")


def send_test_email(recipient_email):
    """Send a test verification email"""
    print("\n" + "="*60)
    print("SENDING TEST EMAIL")
    print("="*60)
    
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("✗ Email credentials not configured in settings.py")
        print("  Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        return
    
    print(f"From: {settings.EMAIL_HOST_USER}")
    print(f"To: {recipient_email}")
    print("Sending...")
    
    try:
        from django.utils import timezone
        
        # Create email context
        context = {
            'user': type('User', (), {
                'name': 'Test User',
                'email': recipient_email
            })(),
            'verification_url': 'http://localhost:8000/register/verify-email/TEST_TOKEN_123456',
            'expiry_days': 7,
            'current_year': timezone.now().year,
        }
        
        html_message = render_to_string('registration/emails/verification_email.html', context)
        subject = '✉️ Verify Your Email - Student Resource Exchange'
        
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body="Please verify your email by clicking the link in this email.",
            from_email=f"Student Resource Exchange <{settings.DEFAULT_FROM_EMAIL}>",
            to=[recipient_email],
            headers={
                'X-Priority': '1',
                'X-MSMail-Priority': 'High',
                'Importance': 'high',
            }
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)
        
        print("✓ Test email sent successfully!")
        print(f"  Check your inbox: {recipient_email}")
        print("  Don't forget to check spam folder!")
        
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        print("\nTroubleshooting:")
        print("  1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py")
        print("  2. Ensure you're using Gmail App Password (not regular password)")
        print("  3. Check your internet connection")
        print("  4. Verify port 587 is not blocked by firewall")


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("EMAIL VERIFICATION TESTING UTILITY")
    print("Student Resource Exchange")
    print("="*60)
    
    # Test email validation
    test_email_validation()
    
    # Test email template
    test_email_template()
    
    # Ask to send test email
    print("\n" + "="*60)
    print("Would you like to send a test email?")
    send_test = input("Enter recipient email (or press Enter to skip): ").strip()
    
    if send_test:
        send_test_email(send_test)
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
