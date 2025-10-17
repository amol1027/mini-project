from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from registration.models import User

def login_view(request):
    """
    Handle user login
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            try:
                # Get user by email
                user = User.objects.get(email=email)
                
                # Check password
                if user.check_password(password):
                    # Store user info in session
                    request.session['user_id'] = user.id
                    request.session['user_email'] = user.email
                    request.session['user_name'] = user.name or user.email
                    request.session['is_admin'] = user.is_admin
                    
                    # Set session expiry
                    if remember_me:
                        request.session.set_expiry(1209600)  # 2 weeks
                    else:
                        request.session.set_expiry(0)  # Browser close
                    
                    messages.success(request, f'Welcome back, {user.name or user.email}!')
                    
                    # Redirect based on user type
                    if user.is_admin:
                        return redirect('dashboard:dashboard')  # Admin goes to dashboard
                    else:
                        return redirect('profile:profile')  # Regular user goes to profile
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'login/login.html', {'form': form})

def logout_view(request):
    """
    Handle user logout
    """
    # Clear session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing:landing')
