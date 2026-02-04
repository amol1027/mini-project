# Google OAuth Setup Guide

## ✅ What's Already Done

All the code integration is complete! Here's what has been implemented:

1. ✅ Installed `social-auth-app-django` package
2. ✅ Updated `settings.py` with authentication backends and Google OAuth configuration
3. ✅ Added social_django URLs to the main URLconf
4. ✅ Created custom pipeline (`login/social_pipeline.py`) to integrate with your User model
5. ✅ Added `is_google_user` field to User model
6. ✅ Updated login template with Google Sign-in button
7. ✅ Ran all migrations successfully

## 🔧 Required: Get Google OAuth Credentials

You need to complete this step to make Google login work:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "Student Resource Exchange")
4. Click "Create"

### Step 2: Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in required fields:
   - App name: Student Resource Exchange
   - User support email: your email
   - Developer contact information: your email
4. Click "Save and Continue"
5. Skip "Scopes" (click "Save and Continue")
6. Add test users if needed (optional for development)
7. Click "Save and Continue"

### Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: **Web application**
4. Name: "Student Resource Exchange Web Client"
5. **Authorized JavaScript origins:**
   - `http://localhost:8000`
   - `http://127.0.0.1:8000`
   - Add your ngrok URLs when testing online (e.g., `https://your-subdomain.ngrok-free.app`)

6. **Authorized redirect URIs:** (CRITICAL - Must match exactly!)
   - `http://localhost:8000/auth/complete/google-oauth2/`
   - `http://127.0.0.1:8000/auth/complete/google-oauth2/`
   - Add ngrok URLs: `https://your-subdomain.ngrok-free.app/auth/complete/google-oauth2/`

7. Click "Create"
8. **SAVE** the Client ID and Client Secret that appear

### Step 5: Update Your Settings

Open `Student_Resource_Exchange/settings.py` and replace these lines (around line 194):

```python
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id-here.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret-here'
```

With your actual credentials:

```python
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'YOUR_ACTUAL_CLIENT_SECRET'
```

### Step 6: Update CSRF Trusted Origins (if using ngrok)

If you're testing with ngrok, add your ngrok URL to `CSRF_TRUSTED_ORIGINS` in settings.py:

```python
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
    'https://*.ngrok-free.dev',
    'https://your-specific-subdomain.ngrok-free.app',  # Add your specific URL
]
```

## 🧪 Testing

1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. Go to: http://localhost:8000/login/

3. Click the "Sign in with Google" button

4. You should be redirected to Google's login page

5. After authorizing, you'll be redirected back and logged in!

## 🔍 Troubleshooting

### Error: "redirect_uri_mismatch"
- **Cause:** The redirect URI in your Google Console doesn't match exactly
- **Fix:** Make sure the redirect URI includes the trailing slash: `/auth/complete/google-oauth2/`
- **Fix:** Protocol must match (http vs https)

### Error: "Invalid client"
- **Cause:** Wrong Client ID or Secret
- **Fix:** Double-check the credentials in settings.py match Google Console

### User created but not logged in
- **Cause:** Session might not be set correctly
- **Fix:** Check the `social_pipeline.py` is setting session variables

### Google returns "Access Blocked: This app's request is invalid"
- **Cause:** OAuth consent screen not configured or app not verified
- **Fix:** Complete the OAuth consent screen configuration
- **Fix:** Add your email as a test user in Google Console

## 📝 How It Works

1. User clicks "Sign in with Google" on your login page
2. User is redirected to Google's OAuth page
3. User authorizes your app
4. Google redirects back to: `http://localhost:8000/auth/complete/google-oauth2/`
5. Our custom pipeline (`login/social_pipeline.py`) runs:
   - Checks if user exists by email
   - If exists: logs them in
   - If new: creates a new User in your database with `is_google_user=True`
6. Session is set with user info (compatible with your existing session auth)
7. User is redirected to `/products/`

## 🔒 Security Notes

### For Production:

1. **NEVER commit credentials to Git:**
   ```python
   # Use environment variables
   import os
   SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH_KEY')
   SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH_SECRET')
   ```

2. **Update redirect URIs** in Google Console with your production domain

3. **Verify OAuth consent screen** for production use (requires Google verification)

4. **Set DEBUG = False** and update ALLOWED_HOSTS

## 🎨 Customization

### Change Redirect URL After Login

Edit in `settings.py`:
```python
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/dashboard/'  # Change to any URL
```

### Request Additional Information from Google

Edit in `settings.py`:
```python
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/user.birthday.read',  # Add birthday
    'https://www.googleapis.com/auth/user.phonenumbers.read',  # Add phone
]
```

### Customize User Creation

Edit `login/social_pipeline.py` to add custom logic during user creation.

## 📚 Additional Resources

- [Social Auth Documentation](https://python-social-auth.readthedocs.io/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django Social Auth Tutorial](https://python-social-auth.readthedocs.io/en/latest/configuration/django.html)

## ✨ Features

- ✅ Seamless Google login integration
- ✅ Automatic user creation for new Google users
- ✅ Compatible with existing session-based authentication
- ✅ Email verification automatically handled (Google verifies emails)
- ✅ Users can still use traditional login/register
- ✅ Admin/regular user roles preserved
- ✅ Beautiful Google button with official branding

---

**Need Help?** Check the troubleshooting section above or refer to the documentation links.
