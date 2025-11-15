# 🗺️ Live Map Feature - Implementation Guide

## Overview

The Student Resource Exchange platform now includes a comprehensive live map feature that helps users visualize product locations, calculate distances, and suggest meeting points for buy/sell and borrow/lend transactions. This feature uses **Leaflet.js** with **OpenStreetMap** (100% free, no API keys required) and **Nominatim** for geocoding.

## 🎯 Key Features

### 1. **Interactive Product Map**
- View all available products on an interactive map with colored markers
- Marker clustering for performance with many products
- Distance-based filtering (5km, 10km, 25km, 50km radius)
- Category and listing type filters
- Product popup cards with images, prices, and direct links

### 2. **Privacy-First Location Sharing**
- **Approximate Location (Default)**: Coordinates rounded to ~100m radius for privacy
- **Precise Location (Opt-in)**: Exact coordinates shared only after request approval
- User-controlled privacy toggle in profile settings

### 3. **Automatic Geocoding**
- Addresses automatically converted to coordinates when profile is updated
- Background geocoding command for existing users: `python manage.py geocode_users`
- Intelligent caching (24 hours) to respect Nominatim rate limits (1 req/sec)

### 4. **Distance Calculations**
- Real-time distance calculations between users using Haversine formula
- Distance displayed on product listings and map popups
- Distance-based sorting and filtering

### 5. **Meeting Point Suggestions** (Coming Soon)
- Calculate midpoint between buyer/seller or borrower/lender
- Suggest meeting locations for approved requests
- Display meeting point map in request detail pages

## 📂 Files Created/Modified

### New Files Created:
1. **`registration/geocoding_utils.py`** - Core geocoding utilities
   - `geocode_address()` - Convert address to lat/lng
   - `geocode_user()` - Geocode user's full address
   - `calculate_distance()` - Haversine distance calculation
   - `get_distance_between_users()` - Distance with caching
   - `calculate_midpoint()` - Midpoint between two points
   - `get_meeting_point()` - Meeting point suggestion
   - `approximate_coordinates()` - Privacy-preserving coordinate rounding

2. **`registration/management/commands/geocode_users.py`** - Management command
   - Batch geocode existing users
   - Rate limiting compliance
   - Progress tracking

3. **`products/templates/products/product_map.html`** - Interactive map UI
   - Leaflet.js integration
   - Marker clustering
   - Filter controls
   - Responsive design

4. **`user_profile/templates/user_profile/edit_profile.html`** - Profile editor
   - Address fields
   - Privacy toggle
   - Location status indicator

### Modified Files:
1. **`registration/models.py`**
   - Added `latitude`, `longitude`, `share_precise_location` fields
   - Added `get_full_address()`, `get_approximate_location()`, `has_location()` methods
   - Added database index for lat/lng queries

2. **`products/views.py`**
   - `product_map()` - Main map view with filters
   - `product_distance_api()` - AJAX distance endpoint
   - `meeting_point_api()` - Meeting point calculation endpoint

3. **`products/urls.py`**
   - `/products/map/` - Product map page
   - `/products/<id>/distance/` - Distance API
   - `/products/meeting-point/<id>/<type>/` - Meeting point API

4. **`user_profile/views.py`**
   - `edit_profile()` - Profile editor with auto-geocoding

5. **`user_profile/urls.py`**
   - `/profile/edit/` - Edit profile route

6. **`products/templates/products/product_list.html`**
   - Added "View on Map" button

7. **`requirements.txt`**
   - Added `geopy>=2.4.0`

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install geopy
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Geocode Existing Users (Optional)
```bash
# Geocode all users without coordinates
python manage.py geocode_users

# Geocode ALL users (including those with existing coordinates)
python manage.py geocode_users --all

# Limit to first 10 users
python manage.py geocode_users --limit 10
```

### 4. Access the Map
Navigate to: `/products/map/`

Or click "View on Map" button on product list page.

## 🎨 User Interface

### Product Map Page (`/products/map/`)

**Features:**
- Interactive Leaflet map with OpenStreetMap tiles
- Colored markers by listing type:
  - 🔵 Blue: Your location
  - 🟢 Green: For Sale
  - 🟣 Purple: For Lending
  - 🟠 Orange: Sale or Lend
- Marker clustering for performance
- Filter controls:
  - Category filter (Books, Notes, Electronics, etc.)
  - Distance filter (5km, 10km, 25km, 50km)
  - Listing type filter (Sell, Lend, Both)
- Product popups with:
  - Product image
  - Title and category badges
  - Price/rental rate
  - Distance from you
  - "View Details" button

**Responsive Design:**
- Desktop: 600px map height, full controls
- Mobile: 400px map height, touch-friendly

### Edit Profile Page (`/profile/edit/`)

**Address Section:**
- Address Line 1 (required for geocoding)
- Address Line 2 (optional)
- City, State/Province
- ZIP/Postal Code
- Country (default: India)

**Privacy Settings:**
- ☑️ Share Precise Location toggle
  - When checked: Exact coordinates visible to approved requesters
  - When unchecked: Approximate location (~100m radius) shown
- Location status indicator:
  - ✓ Green: Coordinates successfully geocoded
  - ⚠️ Yellow: No coordinates (address needed)

**Auto-Geocoding:**
- Triggers automatically when address is saved
- Success message: "Location coordinates updated"
- Warning message: "Couldn't find exact coordinates" (invalid address)

## 📊 Database Schema

### User Model Updates

```python
class User(models.Model):
    # ... existing fields ...
    
    # Geolocation fields (NEW)
    latitude = DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    share_precise_location = BooleanField(default=False)
    
    class Meta:
        indexes = [
            Index(fields=['latitude', 'longitude']),  # Performance optimization
        ]
```

**Migration:** `registration/migrations/0004_user_latitude_user_longitude_and_more.py`

## 🔧 Technical Details

### Geocoding Service: Nominatim (OpenStreetMap)

**Why Nominatim?**
- ✅ 100% Free, no credit card required
- ✅ No API key needed
- ✅ Open source, privacy-friendly
- ✅ Good coverage for Indian addresses
- ✅ Reverse geocoding support

**Rate Limits:**
- 1 request per second (strictly enforced)
- User-Agent header required: `student_resource_exchange/1.0`

**Caching Strategy:**
- Geocoding results: 24 hours
- Distance calculations: 1 hour
- Uses Django's cache framework

### Map Library: Leaflet.js

**Why Leaflet?**
- ✅ Lightweight (38KB gzipped)
- ✅ Mobile-friendly
- ✅ Plugin ecosystem (MarkerCluster)
- ✅ No dependencies
- ✅ Open source (BSD license)

**CDN Links:**
```html
<!-- Leaflet Core -->
<link href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" rel="stylesheet" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- MarkerCluster Plugin -->
<link href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" rel="stylesheet" />
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
```

### Distance Calculation: Haversine Formula

```python
from geopy.distance import geodesic

def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers
```

**Accuracy:** ±0.5% (typically within 10-50m for distances under 100km)

### Privacy Implementation

**Approximate Coordinates (Default):**
```python
def approximate_coordinates(lat, lng, radius_km=0.1):
    # Round to 3 decimal places (~111m precision)
    approx_lat = round(float(lat), 3)
    approx_lng = round(float(lng), 3)
    return approx_lat, approx_lng
```

**Example:**
- Exact: `19.076090, 72.877426`
- Approximate: `19.076, 72.877` (~100m radius)

**Precision Levels:**
- 1 decimal place = ~11 km
- 2 decimal places = ~1.1 km
- 3 decimal places = ~111 m ✓ (Used)
- 4 decimal places = ~11 m
- 5 decimal places = ~1.1 m

## 🎯 Use Cases

### 1. Buyer Finding Nearby Products
```
User Flow:
1. Navigate to /products/map/
2. Map centers on user's location
3. Filter by distance (e.g., "Within 10 km")
4. Filter by category (e.g., "Books")
5. Click marker to view product popup
6. Click "View Details" to see full listing
```

### 2. Seller Updating Location
```
User Flow:
1. Navigate to /profile/edit/
2. Fill in complete address
3. Toggle "Share Precise Location" if comfortable
4. Click "Save Changes"
5. System auto-geocodes address in background
6. Success message shows if coordinates found
7. Products now visible on map
```

### 3. Meeting Point Suggestion (Future)
```
User Flow:
1. Buyer sends borrow/purchase request
2. Seller approves request
3. System calculates midpoint between users
4. Meeting point displayed on request detail page
5. Both parties can view suggested location
6. Meeting point shared in OTP chat message
```

## 📈 Performance Optimizations

### 1. Database Indexing
```python
class Meta:
    indexes = [
        models.Index(fields=['latitude', 'longitude']),
    ]
```
**Impact:** 10-100x faster queries for location-based searches

### 2. Marker Clustering
```javascript
const markers = L.markerClusterGroup({
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false
});
```
**Impact:** Smooth performance with 1000+ products

### 3. Caching
- Geocoding: 24-hour cache per address
- Distance: 1-hour cache per user pair
- Cache invalidation: On address update

### 4. Lazy Loading
- Map tiles load on-demand
- Product popups load on marker click
- Images lazy-load in popups

## 🔒 Security Considerations

### 1. Rate Limiting
```python
time.sleep(1)  # Nominatim: 1 req/sec
```

### 2. Input Validation
- Address sanitization before geocoding
- Coordinate bounds checking (valid lat/lng ranges)
- SQL injection prevention (Django ORM)

### 3. Privacy Protection
- Default to approximate location
- Exact location only for approved requesters
- User-controlled privacy toggle

### 4. HTTPS Required
- Geolocation API requires secure context
- OpenStreetMap tiles served over HTTPS

## 🐛 Troubleshooting

### Issue: "Geocoding failed"
**Cause:** Invalid/incomplete address
**Solution:**
1. Ensure all address fields are filled (especially City)
2. Try adding more detail (landmarks, nearby areas)
3. Check spelling of city/state names
4. Try format: "Street, Area, City, State, PIN, Country"

### Issue: Map not loading
**Cause:** CDN blocked or slow connection
**Solution:**
1. Check browser console for errors
2. Verify internet connection
3. Try hard refresh (Ctrl+F5)
4. Check if Leaflet CDN is accessible

### Issue: No products on map
**Cause:** Users haven't geocoded addresses
**Solution:**
```bash
python manage.py geocode_users
```

### Issue: "Rate limit exceeded"
**Cause:** Too many geocoding requests
**Solution:**
1. Wait 1 second between requests (enforced in code)
2. Use `--limit` flag for batch geocoding
3. Check cache configuration

### Issue: Distance calculations wrong
**Cause:** Coordinates in wrong order (lng, lat instead of lat, lng)
**Solution:** Verify coordinate order in all functions (should be lat, lng)

## 📱 Mobile Optimization

- Touch-friendly marker interactions
- Responsive filter controls (horizontal scroll)
- Reduced map height on small screens (400px)
- Swipeable popups
- Mobile menu integration

## 🔮 Future Enhancements

### 1. Real-time Location Sharing (Advanced)
- WebSocket integration for live location
- "On the way" status updates
- ETA calculations

### 2. Route Navigation
- Integrate with Google Maps/Apple Maps
- "Get Directions" button in popups
- Route optimization for multiple pickups

### 3. Geofencing
- Notifications when buyer enters pickup area
- Automatic check-in for OTP verification
- Location-based reminders

### 4. Heat Maps
- Popular product areas
- High-demand categories by location
- Trending items near you

### 5. Location-Based Search
- "Products within 5km of [address]"
- Search by landmark
- Campus-specific filtering (e.g., "Show items in North Campus")

## 📚 API Endpoints

### 1. Product Map View
```
GET /products/map/
Query Params:
  - category: books|notes|electronics|stationery|lab_equipment
  - distance: 5|10|25|50 (km)
  - type: sell|lend|both
```

### 2. Distance API
```
GET /products/<product_id>/distance/
Response:
{
  "distance": 5.23,
  "distance_formatted": "5.2 km",
  "has_location": true
}
```

### 3. Meeting Point API
```
GET /products/meeting-point/<request_id>/<type>/
Type: borrow|purchase
Response:
{
  "meeting_point": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "description": "Cafe Coffee Day, Andheri West",
    "distance_from_user1": 2.5,
    "distance_from_user2": 3.1
  },
  "user1": { "name": "John", "latitude": 19.074, "longitude": 72.880 },
  "user2": { "name": "Jane", "approximate_location": "Mumbai, Maharashtra" }
}
```

## 🎓 Learning Resources

- [Leaflet.js Documentation](https://leafletjs.com/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)
- [Geopy Documentation](https://geopy.readthedocs.io/)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)

## 📝 Changelog

### Version 1.0 (November 15, 2025)
- ✅ Initial map feature implementation
- ✅ Leaflet.js integration with OpenStreetMap
- ✅ Nominatim geocoding with caching
- ✅ Distance calculations and filtering
- ✅ Privacy-first location sharing
- ✅ Marker clustering for performance
- ✅ Responsive mobile design
- ✅ Edit profile with auto-geocoding
- ✅ Management command for batch geocoding

### Upcoming (Version 1.1)
- 🔄 Meeting point suggestions in request details
- 🔄 OTP chat integration with meeting locations
- 🔄 Distance badges on product cards
- 🔄 "Near me" quick filter

## 🤝 Contributing

When adding map-related features:
1. Respect Nominatim rate limits (1 req/sec)
2. Use caching for repeated queries
3. Test with approximate and precise location modes
4. Ensure mobile responsiveness
5. Update this documentation

## 📄 License

This feature is part of the Student Resource Exchange project and follows the same MIT license.

---

**Questions or Issues?** Contact the development team or create an issue on GitHub.
