from django.shortcuts import render, redirect

def landing_page(request):
    # If user is already logged in, redirect them to appropriate page
    if request.session.get('user_id'):
        # Check if user is admin
        if request.session.get('is_admin', False):
            return redirect('dashboard:dashboard')  # Redirect admin to dashboard
        else:
            return redirect('profile:profile')  # Redirect regular user to profile
    
    return render(request, 'landing/landing.html')
