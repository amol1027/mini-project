"""
Geocoding utilities for Student Resource Exchange
Uses Nominatim (OpenStreetMap) - free, no API key required
"""
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from django.core.cache import cache
import hashlib
import time
import logging

logger = logging.getLogger(__name__)

# Initialize geocoder with user agent
geolocator = Nominatim(user_agent="student_resource_exchange/1.0")

def get_address_hash(address):
    """Create hash of address for caching"""
    return hashlib.md5(address.encode()).hexdigest()

def geocode_address(address, use_cache=True):
    """
    Convert address to latitude/longitude coordinates
    
    Args:
        address: Full address string
        use_cache: Use cached results if available
        
    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails
    """
    if not address or not address.strip():
        return None, None
    
    # Check cache first
    if use_cache:
        cache_key = f'geocode_{get_address_hash(address)}'
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Geocoding cache hit for hash: {get_address_hash(address)}")
            return cached_result
    
    try:
        # Nominatim rate limit: 1 request per second
        time.sleep(1)
        
        location = geolocator.geocode(address, timeout=10)
        
        if location:
            lat, lng = location.latitude, location.longitude
            logger.info(f"Geocoded hash: {get_address_hash(address)} -> ({lat}, {lng})")
            
            # Cache for 24 hours
            if use_cache:
                cache_key = f'geocode_{get_address_hash(address)}'
                cache.set(cache_key, (lat, lng), 86400)
            
            return lat, lng
        else:
            logger.warning(f"Geocoding failed: No results for hash {get_address_hash(address)}")
            return None, None
            
    except GeocoderTimedOut:
        logger.error(f"Geocoding timeout for hash: {get_address_hash(address)}")
        return None, None
    except GeocoderServiceError as e:
        logger.error(f"Geocoding service error: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected geocoding error: {str(e)}")
        return None, None

def geocode_user(user):
    """
    Geocode user's address and update their coordinates
    
    Args:
        user: User model instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    address = user.get_full_address()
    if not address:
        logger.warning(f"User {user.id} has no address to geocode")
        return False
    
    lat, lng = geocode_address(address)
    
    if lat and lng:
        user.latitude = lat
        user.longitude = lng
        user.save(update_fields=['latitude', 'longitude', 'updated_at'])
        logger.info(f"Updated coordinates for user {user.id}")
        return True
    else:
        logger.warning(f"Failed to geocode user {user.id}")
        return False

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        float: Distance in kilometers
    """
    if None in (lat1, lon1, lat2, lon2):
        return None
    
    try:
        point1 = (float(lat1), float(lon1))
        point2 = (float(lat2), float(lon2))
        distance = geodesic(point1, point2).kilometers
        return round(distance, 2)
    except Exception as e:
        logger.error(f"Distance calculation error: {str(e)}")
        return None

def get_distance_between_users(user1, user2, use_cache=True):
    """
    Calculate distance between two users
    
    Args:
        user1, user2: User model instances
        use_cache: Use cached results
        
    Returns:
        float: Distance in kilometers or None
    """
    if not user1.has_location() or not user2.has_location():
        return None
    
    # Check cache
    if use_cache:
        cache_key = f'distance_{min(user1.id, user2.id)}_{max(user1.id, user2.id)}'
        cached_distance = cache.get(cache_key)
        if cached_distance is not None:
            return cached_distance
    
    distance = calculate_distance(
        user1.latitude, user1.longitude,
        user2.latitude, user2.longitude
    )
    
    # Cache for 1 hour
    if use_cache and distance is not None:
        cache_key = f'distance_{min(user1.id, user2.id)}_{max(user1.id, user2.id)}'
        cache.set(cache_key, distance, 3600)
    
    return distance

def calculate_midpoint(lat1, lon1, lat2, lon2):
    """
    Calculate midpoint between two coordinates
    
    Args:
        lat1, lon1: First point
        lat2, lon2: Second point
        
    Returns:
        tuple: (latitude, longitude) of midpoint
    """
    if None in (lat1, lon1, lat2, lon2):
        return None, None
    
    try:
        mid_lat = (float(lat1) + float(lat2)) / 2
        mid_lon = (float(lon1) + float(lon2)) / 2
        return round(mid_lat, 6), round(mid_lon, 6)
    except Exception as e:
        logger.error(f"Midpoint calculation error: {str(e)}")
        return None, None

def get_meeting_point(user1, user2):
    """
    Suggest meeting point between two users
    
    Args:
        user1, user2: User model instances
        
    Returns:
        dict: Meeting point info with lat, lng, description
    """
    if not user1.has_location() or not user2.has_location():
        return None
    
    mid_lat, mid_lon = calculate_midpoint(
        user1.latitude, user1.longitude,
        user2.latitude, user2.longitude
    )
    
    if mid_lat is None:
        return None
    
    try:
        # Reverse geocode to get location name
        time.sleep(1)  # Rate limit
        location = geolocator.reverse(f"{mid_lat}, {mid_lon}", timeout=10)
        
        address = location.address if location else "Meeting point"
        
        return {
            'latitude': mid_lat,
            'longitude': mid_lon,
            'description': address,
            'distance_from_user1': calculate_distance(
                user1.latitude, user1.longitude, mid_lat, mid_lon
            ),
            'distance_from_user2': calculate_distance(
                user2.latitude, user2.longitude, mid_lat, mid_lon
            )
        }
    except Exception as e:
        logger.error(f"Meeting point error: {str(e)}")
        return {
            'latitude': mid_lat,
            'longitude': mid_lon,
            'description': 'Meeting point (coordinates only)',
            'distance_from_user1': None,
            'distance_from_user2': None
        }

def approximate_coordinates(lat, lng, radius_km=0.1):
    """
    Approximate coordinates for privacy (round to ~100m)
    
    Args:
        lat, lng: Exact coordinates
        radius_km: Approximation radius in km
        
    Returns:
        tuple: Approximated (lat, lng)
    """
    if lat is None or lng is None:
        return None, None
    
    # Round to 3 decimal places (~111m precision)
    approx_lat = round(float(lat), 3)
    approx_lng = round(float(lng), 3)
    
    return approx_lat, approx_lng

def reverse_geocode(lat, lng, use_cache=True):
    """
    Convert coordinates to address details
    
    Args:
        lat, lng: Coordinates
        use_cache: Use cached results if available
        
    Returns:
        dict: Address components or None
    """
    if lat is None or lng is None:
        return None
        
    # Check cache first
    cache_key = f'reverse_geocode_{lat}_{lng}'
    if use_cache:
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Reverse geocoding cache hit for: {lat}, {lng}")
            return cached_result
            
    try:
        # Nominatim rate limit: 1 request per second
        time.sleep(1)
        
        location = geolocator.reverse(f"{lat}, {lng}", timeout=10, language='en')
        
        if location and location.raw.get('address'):
            address = location.raw['address']
            
            # Construct address line 1
            house_number = address.get('house_number', '')
            road = address.get('road') or address.get('pedestrian') or address.get('footway') or address.get('street') or ''
            
            if house_number and road:
                address_line1 = f"{house_number} {road}"
            else:
                address_line1 = house_number or road or ''
                
            # If still empty, try to use the name of the place (e.g. building name)
            if not address_line1:
                 address_line1 = address.get('amenity') or address.get('building') or ''

            # Map Nominatim fields to our model fields
            result = {
                'address_line1': address_line1,
                'city': address.get('city') or address.get('town') or address.get('village') or address.get('hamlet') or address.get('suburb') or '',
                'state_province': address.get('state') or address.get('region') or '',
                'zip_postal_code': address.get('postcode') or '',
                'country': address.get('country') or '',
                'full_address': location.address
            }
            
            # Cache for 24 hours
            if use_cache:
                cache.set(cache_key, result, 86400)
                
            return result
        else:
            logger.warning(f"Reverse geocoding failed: No results for {lat}, {lng}")
            return None
            
    except Exception as e:
        logger.error(f"Reverse geocoding error: {str(e)}")
        return None
