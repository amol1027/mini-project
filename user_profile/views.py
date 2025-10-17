from django.shortcuts import render, redirect
from django.contrib import messages
from registration.models import User

def profile_view(request):
    """
    User profile view - Shows user's own information
    """
    # Check if user is logged in
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access your profile.')
        return redirect('login:login')
    
    # Get current user
    try:
        user = User.objects.get(id=request.session['user_id'])
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        request.session.flush()
        return redirect('login:login')
    
    # Calculate profile completion
    fields_filled = 0
    total_fields = 12  # Total important fields to track
    
    if user.name:
        fields_filled += 1
    if user.email:
        fields_filled += 1
    if user.college_id:
        fields_filled += 1
    if user.email_verified:
        fields_filled += 1
    if user.address_line1:
        fields_filled += 1
    if user.address_line2:
        fields_filled += 1
    if user.city:
        fields_filled += 1
    if user.state_province:
        fields_filled += 1
    if user.zip_postal_code:
        fields_filled += 1
    if user.country:
        fields_filled += 1
    if user.rating > 0:
        fields_filled += 1
    
    # Always count password as filled
    fields_filled += 1
    
    profile_completion = int((fields_filled / total_fields) * 100)
    
    context = {
        'user': user,
        'profile_completion': profile_completion,
    }
    
    return render(request, 'user_profile/profile.html', context)
