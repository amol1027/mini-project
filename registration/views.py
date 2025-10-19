from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .models import User

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
            
            messages.success(request, 'Registration successful! You can now log in with your credentials.')
            return redirect('login:login')  # Redirect to login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
