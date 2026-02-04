# Email Verification Setup Guide

## Gmail Configuration for Email Verification

This project uses Gmail's SMTP service to send email verification emails. Follow these steps to configure it:

### 1. Enable Gmail App Password

Since Google disabled "less secure app access," you need to create an App Password:

1. **Enable 2-Factor Authentication** on your Google account if not already enabled:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" as the app and "Windows Computer" as the device (or any)
   - Click "Generate"
   - Copy the 16-character password (without spaces)

### 2. Update Django Settings

Open `Student_Resource_Exchange/settings.py` and update the email configuration:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'  # The App Password you generated
```

**⚠️ Important Security Notes:**
- Never commit your real credentials to version control
- Consider using environment variables for production:
  ```python
  EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
  ```

### 3. Test Email Configuration

Run this command to test if emails are working:

```bash
python manage.py shell
```

Then in the Python shell:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from Student Resource Exchange.',
    settings.DEFAULT_FROM_EMAIL,
    ['recipient@example.com'],
    fail_silently=False,
)
```

If successful, you should receive the test email!

## How Email Verification Works

### Registration Flow
1. User registers with email and password
2. System creates user account with `email_verified=False`
3. System generates a unique verification token
4. System sends verification email with link
5. User clicks verification link
6. System verifies token and marks email as verified
7. User can now log in

### Login Flow
- **Google users**: Automatically verified (email_verified=True)
- **Email/password users**: Must verify email before login
- If unverified user tries to log in, they're redirected to resend verification page

### Available URLs

- **Register**: `/register/`
- **Verify Email**: `/register/verify-email/<token>/`
- **Resend Verification**: `/register/resend-verification/`
- **Login**: `/login/`

## Email Verification Features

### Security Features
- Tokens expire after 7 days (configurable in settings)
- One-time use tokens (can't be reused)
- Secure random token generation
- Email verification only required for non-Google users

### User Experience
- Clear success/error messages
- Easy resend verification option
- Professional HTML email template
- Mobile-responsive email design

## Customization

### Change Token Expiry Time

Edit in `settings.py`:
```python
EMAIL_VERIFICATION_TIMEOUT_DAYS = 7  # Change to desired number of days
```

### Customize Email Template

Edit: `registration/templates/registration/emails/verification_email.html`

The template uses these variables:
- `user` - User object
- `verification_url` - Full verification link
- `expiry_days` - Number of days until link expires

### Clean Up Expired Tokens

Add this to your periodic tasks (Celery):

```python
from registration.email_utils import delete_expired_tokens

# Run daily
delete_expired_tokens()
```

## Troubleshooting

### Emails Not Sending

1. **Check Gmail credentials**: Ensure App Password is correct
2. **Check spam folder**: Verification emails might go to spam
3. **Check firewall**: Port 587 must be open
4. **Check logs**: Look for error messages in console

### "SMTPAuthenticationError"

- Your App Password is incorrect
- 2-Factor Authentication is not enabled
- You're using regular password instead of App Password

### "Connection refused"

- Your firewall is blocking port 587
- Gmail SMTP is temporarily unavailable
- Check your internet connection

## Production Recommendations

1. **Use environment variables** for email credentials
2. **Use a dedicated email service** like SendGrid or AWS SES for better deliverability
3. **Implement rate limiting** on resend verification endpoint
4. **Set up email monitoring** to track delivery rates
5. **Configure HTTPS** and set `EMAIL_USE_SSL = True` if needed

## Example: Environment Variables Setup

Create a `.env` file (add to `.gitignore`):
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Install python-decouple:
```bash
pip install python-decouple
```

Update `settings.py`:
```python
from decouple import config

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

## Database Schema

### EmailVerificationToken Model

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | ForeignKey | Reference to User |
| token | CharField | Unique verification token |
| created_at | DateTimeField | Token creation time |
| expires_at | DateTimeField | Token expiration time |
| is_used | BooleanField | Whether token has been used |

## Additional Features to Consider

1. **Email Change Verification**: Verify new email when user changes their email
2. **Welcome Email**: Send welcome email after verification
3. **Reminder Emails**: Send reminder if user hasn't verified after X days
4. **Admin Dashboard**: View verification statistics
5. **Bulk Operations**: Admin can manually verify users

---

**Need Help?**
Check Django documentation on sending emails: https://docs.djangoproject.com/en/5.2/topics/email/
