"""
Custom social auth pipeline for integrating Google OAuth with custom User model.
This pipeline creates or updates users in the registration.models.User model.
"""
from registration.models import User
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

DjangoUser = get_user_model()


def handle_duplicate_social_auth(backend, uid, user=None, social=None, *args, **kwargs):
    """
    Handle cases where a social auth account (Google) is already associated with a user.
    This prevents IntegrityError when trying to create duplicate UserSocialAuth records.
    
    If the social auth exists but is associated with a different user, we need to decide:
    - If the current user is None (new login), use the existing association
    - If there's a conflict, prefer the existing association
    
    Args:
        backend: The authentication backend (GoogleOAuth2)
        uid: The unique ID from the provider
        user: Current Django user if exists
        social: Existing UserSocialAuth record if found
        
    Returns:
        dict or None: Returns the existing user if found, None otherwise
    """
    from social_django.models import UserSocialAuth
    
    # Check if this uid already exists for this provider
    try:
        existing_social = UserSocialAuth.objects.get(provider=backend.name, uid=uid)
        
        # If we found an existing social auth record
        if existing_social.user:
            # Return the user associated with this social auth
            # This will be used by the rest of the pipeline
            return {
                'user': existing_social.user,
                'social': existing_social,
                'is_new': False
            }
    except UserSocialAuth.DoesNotExist:
        # No duplicate, continue normally
        pass
    
    return None


def create_custom_user(strategy, details, backend, user=None, *args, **kwargs):
    """
    Create or retrieve both Django's User and our custom User model.
    
    Social-auth requires a Django User for UserSocialAuth relationships,
    but we also maintain our custom User model for the application logic.
    
    Args:
        strategy: The social auth strategy being used
        details: User details from the OAuth provider (Google)
        backend: The authentication backend (GoogleOAuth2)
        user: Existing Django user if found
        
    Returns:
        dict: Dictionary with 'is_new' flag and 'user' object
    """
    request = strategy.request if hasattr(strategy, 'request') else None
    
    # Extract user information from Google OAuth response
    email = details.get('email')
    first_name = details.get('first_name', '')
    last_name = details.get('last_name', '')
    full_name = details.get('fullname') or f"{first_name} {last_name}".strip()
    username = email.split('@')[0] if email else get_random_string(10)
    
    if not email:
        # Email is required - if not provided, we can't create/find user
        if request:
            messages.error(request, 'Email is required for registration.')
        return {'is_new': False, 'user': None}
    
    # First, handle Django's User model (required by social_django)
    django_user = None
    if user:
        django_user = user
    else:
        # Try to find or create Django User
        django_user, created = DjangoUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
    
    # Now handle our custom User model
    try:
        # Try to find existing user by email
        custom_user = User.objects.get(email=email)
        
        # Update user info if name wasn't set before
        if not custom_user.name and full_name:
            custom_user.name = full_name
            custom_user.save()
        
        # Set session data for compatibility with existing session-based auth
        if request:
            request.session['user_id'] = custom_user.id
            request.session['user_email'] = custom_user.email
            request.session['user_name'] = custom_user.name or custom_user.email
            request.session['is_admin'] = custom_user.is_admin
            request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, f'Welcome back, {custom_user.name or custom_user.email}!')
        
        return {
            'is_new': False,
            'user': django_user,  # Return Django user for social_auth
            'custom_user': custom_user
        }
        
    except User.DoesNotExist:
        # Create new user in our custom User model
        custom_user = User.objects.create(
            email=email,
            name=full_name or username,
            college_id='',  # Will be filled later by user
            is_google_user=True,
            email_verified=True,  # Google has already verified the email
        )
        
        # Set a dummy password hash since Google users don't use passwords
        custom_user.set_password(get_random_string(32))
        custom_user.save()
        
        # Set session data
        if request:
            request.session['user_id'] = custom_user.id
            request.session['user_email'] = custom_user.email
            request.session['user_name'] = custom_user.name
            request.session['is_admin'] = False
            request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, f'Welcome to Student Resource Exchange, {custom_user.name}!')
        
        return {
            'is_new': True,
            'user': django_user,  # Return Django user for social_auth
            'custom_user': custom_user
        }


def redirect_based_on_role(strategy, details, backend, user=None, *args, **kwargs):
    """
    Optional: Redirect users based on their role after authentication.
    This can be used to send admins to dashboard and regular users to products.
    """
    request = strategy.request if hasattr(strategy, 'request') else None
    if request and user:
        custom_user = kwargs.get('custom_user')
        if custom_user and custom_user.is_admin:
            strategy.session_set('next', '/dashboard/')
        else:
            strategy.session_set('next', '/products/')


def associate_custom_user(backend, uid, user=None, social=None, *args, **kwargs):
    """
    Custom associate_user that works with our User model without trying to update
    Django's User model fields like last_login.
    
    This replaces social_core.pipeline.social_auth.associate_user to avoid
    the 'last_login' field error.
    """
    if user and social:
        return None
    
    # If we have a user from create_custom_user, just return it
    if user:
        return {'user': user, 'is_new': kwargs.get('is_new', False)}
    
    return None


def custom_user_details(strategy, details, backend, user=None, *args, **kwargs):
    """
    Update user details only for fields that exist in our custom User model.
    This replaces the default user_details pipeline to avoid errors with 
    fields like 'last_login' that don't exist in our model.
    """
    if not user:
        return
    
    # Only update fields that exist in our User model
    changed = False
    
    # Map social auth details to our User model fields
    if details.get('email') and not user.email:
        user.email = details['email']
        changed = True
    
    if details.get('fullname') and not user.name:
        user.name = details['fullname']
        changed = True
    elif not user.name:
        # Try to construct name from first_name and last_name
        first_name = details.get('first_name', '')
        last_name = details.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip()
        if full_name:
            user.name = full_name
            changed = True
    
    # Save only if something changed
    if changed:
        user.save()
    
    return {'user': user}
