from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .models import User, EmailVerificationToken
from .email_utils import send_verification_email
from django.utils import timezone


def register(request):
    """
    Handle user registration
    """
    # If user is already logged in, redirect them to appropriate page
    if request.session.get('user_id'):
        if request.session.get('is_admin', False):
            return redirect('dashboard:dashboard')
        else:
            return redirect('products:product_list')  # Regular users go to products page
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user instance but don't save yet
            user = form.save(commit=False)
            # Hash and set the password
            user.set_password(form.cleaned_data['password'])
            # Save the user
            user.save()
            
            # Send verification email
            if send_verification_email(user, request):
                messages.success(
                    request, 
                    'Registration successful! Please check your email to verify your account. '
                    'You must verify your email before you can log in.'
                )
            else:
                messages.warning(
                    request,
                    'Registration successful but we could not send the verification email. '
                    'Please contact support or try resending the verification email.'
                )
            
            return redirect('login:login')  # Redirect to login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def verify_email(request, token):
    """
    Verify user's email address using the token
    """
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        
        if token_obj.is_valid():
            # Mark token as used
            token_obj.is_used = True
            token_obj.save()
            
            # Mark user's email as verified
            user = token_obj.user
            user.email_verified = True
            user.save()
            
            messages.success(
                request,
                'Email verified successfully! You can now log in to your account.'
            )
            return redirect('login:login')
        else:
            if token_obj.is_used:
                messages.error(request, 'This verification link has already been used.')
            else:
                messages.error(request, 'This verification link has expired. Please request a new one.')
            return redirect('registration:resend_verification')
            
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('login:login')


def resend_verification(request):
    """
    Resend verification email to user
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Check if user is a Google user
            if user.is_google_user:
                messages.info(request, 'Google users do not need email verification.')
                return redirect('login:login')
            
            # Check if already verified
            if user.email_verified:
                messages.info(request, 'Your email is already verified. You can log in.')
                return redirect('login:login')
            
            # Send new verification email
            if send_verification_email(user, request):
                messages.success(
                    request,
                    'Verification email sent! Please check your inbox and spam folder.'
                )
            else:
                messages.error(
                    request,
                    'Failed to send verification email. Please try again later.'
                )
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            messages.success(
                request,
                'If an account exists with that email, a verification link has been sent.'
            )
        
        return redirect('login:login')
    
    return render(request, 'registration/resend_verification.html')
