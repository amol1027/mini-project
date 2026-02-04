from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from registration.models import User
from registration.geocoding_utils import geocode_user, geocode_address, reverse_geocode
from registration.tasks import geocode_user_task
import logging

logger = logging.getLogger(__name__)

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
        name = request.POST.get('name', user.name)
        
        # Validate name
        import re
        if re.search(r'\d', name):
            messages.error(request, 'Name cannot contain numbers.')
            return redirect('user_profile:profile')
            
        user.name = name
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
        
        # Handle explicit location from "Use Current Location"
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        explicit_location = False
        
        if lat and lng:
            try:
                user.latitude = float(lat)
                user.longitude = float(lng)
                explicit_location = True
            except (ValueError, TypeError):
                pass

        # Save user
        user.save()
        
        # Handle address changes and geocoding
        new_address = user.get_full_address()
        if new_address != old_address and not explicit_location:
            if new_address:
                # Address changed to a new value - geocode asynchronously
                geocode_user_task.delay(user.id)
                messages.success(request, 'Profile updated successfully! Location coordinates will be updated shortly.')
            else:
                # Address was cleared - remove stale coordinates
                user.latitude = None
                user.longitude = None
                user.save()
                messages.success(request, 'Profile updated successfully!')
        else:
            # Address unchanged or explicit location used
            messages.success(request, 'Profile updated successfully!')
        
        return redirect('user_profile:profile')
    
    context = {
        'user': user,
    }
    
    return render(request, 'user_profile/edit_profile.html', context)


from django.core.cache import cache

@csrf_protect
def verify_address_api(request):
    """
    API endpoint to verify an address and return coordinates
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if user is logged in
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Rate limiting: 10 requests per minute per user
    rate_limit_key = f"verify_address_limit_{user_id}"
    request_count = cache.get(rate_limit_key, 0)
    if request_count >= 10:
        return JsonResponse({'error': 'Too many requests. Please try again later.'}, status=429)
    
    if request_count == 0:
        cache.set(rate_limit_key, 1, 60)
    else:
        cache.incr(rate_limit_key)
        
    try:
        import json
        data = json.loads(request.body)
        
        # Input validation
        address_parts = [
            str(data.get('address_line1', ''))[:100],
            str(data.get('address_line2', ''))[:100],
            str(data.get('city', ''))[:50],
            str(data.get('state_province', ''))[:50],
            str(data.get('zip_postal_code', ''))[:20],
            str(data.get('country', ''))[:50]
        ]
        
        # Filter out empty parts
        full_address = ", ".join([p for p in address_parts if p and p.strip()])
        
        if not full_address:
            return JsonResponse({'error': 'Address is empty'}, status=400)
            
        if len(full_address) > 500:
             return JsonResponse({'error': 'Address too long'}, status=400)

        # Geocode
        lat, lng = geocode_address(full_address, use_cache=True)
        
        if lat and lng:
            return JsonResponse({
                'success': True,
                'latitude': lat,
                'longitude': lng,
                'formatted_address': full_address # Returning user's own input formatted
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Could not find coordinates for this address'
            })
            
    except Exception as e:
        # Log only the error type, not the content which might contain PII
        logger.error(f"Error in verify_address_api: {type(e).__name__}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_protect
def reverse_geocode_api(request):
    """
    API endpoint to get address from coordinates
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if user is logged in
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Rate limiting: 10 requests per minute per user
    rate_limit_key = f"reverse_geocode_limit_{user_id}"
    request_count = cache.get(rate_limit_key, 0)
    if request_count >= 10:
        return JsonResponse({'error': 'Too many requests. Please try again later.'}, status=429)
    
    if request_count == 0:
        cache.set(rate_limit_key, 1, 60)
    else:
        cache.incr(rate_limit_key)
        
    try:
        import json
        data = json.loads(request.body)
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if not lat or not lng:
            return JsonResponse({'error': 'Coordinates missing'}, status=400)
            
        # Validate coordinates
        try:
            lat = float(lat)
            lng = float(lng)
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                raise ValueError
        except ValueError:
            return JsonResponse({'error': 'Invalid coordinates'}, status=400)

        # Reverse Geocode
        address_data = reverse_geocode(lat, lng, use_cache=True)
        
        if address_data:
            return JsonResponse({
                'success': True,
                'address': address_data
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Could not find address for these coordinates'
            })
            
    except Exception as e:
        logger.error(f"Error in reverse_geocode_api: {type(e).__name__}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
