from django.shortcuts import render, redirect
from django.contrib import messages
from registration.models import User
from registration.geocoding_utils import geocode_user

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
    total_fields = 14  # Total important fields to track (increased from 12)
    
    if user.name:
        fields_filled += 1
    if user.email:
        fields_filled += 1
    if user.college_id:
        fields_filled += 1
    if user.college_name:
        fields_filled += 1
    if user.university_name:
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
    
    # Calculate stroke-dashoffset for circular progress bar
    # Circle circumference = 2 * π * radius = 2 * 3.14159 * 56 ≈ 351.86
    circumference = 351.86
    stroke_offset = circumference - (profile_completion / 100 * circumference)
    
    context = {
        'user': user,
        'profile_completion': profile_completion,
        'stroke_offset': round(stroke_offset, 2),
    }
    
    return render(request, 'user_profile/profile.html', context)


def edit_profile(request):
    """
    Edit user profile with automatic geocoding
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
    
    if request.method == 'POST':
        # Update user fields
        user.name = request.POST.get('name', user.name)
        user.college_name = request.POST.get('college_name', user.college_name)
        user.university_name = request.POST.get('university_name', user.university_name)
        user.college_id = request.POST.get('college_id', user.college_id)
        
        # Address fields - preserve existing values if not in POST
        old_address = user.get_full_address()
        user.address_line1 = request.POST.get('address_line1', user.address_line1)
        user.address_line2 = request.POST.get('address_line2', user.address_line2)
        user.city = request.POST.get('city', user.city)
        user.state_province = request.POST.get('state_province', user.state_province)
        user.zip_postal_code = request.POST.get('zip_postal_code', user.zip_postal_code)
        user.country = request.POST.get('country', user.country)
        
        # Privacy setting - handle both 'true' (checked) and 'false' (hidden fallback)
        # When checkbox is checked, POST contains both 'false' (hidden) and 'true' (checkbox)
        # When unchecked, POST contains only 'false' (hidden)
        user.share_precise_location = 'true' in request.POST.getlist('share_precise_location')
        
        # Save user
        user.save()
        
        # Handle address changes and geocoding
        new_address = user.get_full_address()
        if new_address != old_address:
            if new_address:
                # Address changed to a new value - geocode it
                geocode_success = geocode_user(user)
                if geocode_success:
                    messages.success(request, 'Profile updated successfully! Location coordinates updated.')
                else:
                    messages.warning(request, 'Profile updated, but we couldn\'t find exact coordinates for your address.')
            else:
                # Address was cleared - remove stale coordinates
                user.latitude = None
                user.longitude = None
                user.save()
                messages.success(request, 'Profile updated successfully!')
        else:
            # Address unchanged
            messages.success(request, 'Profile updated successfully!')
        
        return redirect('user_profile:profile')
    
    context = {
        'user': user,
    }
    
    return render(request, 'user_profile/edit_profile.html', context)
