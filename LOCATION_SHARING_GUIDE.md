# Location Sharing for Approved Requests - User Guide

## Overview

The location sharing feature allows users to share their precise location with their transaction partners **only after a request has been approved**. This enhances the privacy-first approach by giving users granular control over who can see their exact location and when.

## Key Features

### 1. **Per-Request Location Control**
- Users can toggle location sharing for each individual approved request
- Location sharing is **OFF by default** for all requests
- Only users involved in the specific request can see each other's location
- Works for both borrow/lend and buy/sell transactions

### 2. **Privacy Levels**

#### Approximate Location (Default)
- Shown to all users viewing products on the map
- Precision: ~100-111 meters (3 decimal places)
- Example: Instead of "123.456789", shows "123.457"
- Visible as: "Approximate area: [City/Region]"

#### Precise Location (Opt-in)
- Only visible when user explicitly enables sharing for a specific request
- Full GPS precision (6 decimal places)
- Shows exact address
- Can be toggled on/off at any time during the transaction

### 3. **Meeting Point Suggestion**
- Automatically calculates midpoint between two parties
- Reverse geocodes to provide readable address
- Shows distance from your location
- Interactive map with color-coded markers:
  - 🔵 Blue: Your location
  - 🟢 Green: Other party (if sharing precise location)
  - 🟠 Orange: Suggested meeting point

## How to Use

### For Borrowers/Buyers

1. **Submit a Request**
   - Browse products and create a borrow/purchase request
   - Request goes to the lender/seller for approval

2. **After Approval**
   - Location sharing section appears on the request detail page
   - By default, only your approximate location is visible

3. **Enable Location Sharing (Optional)**
   - Toggle the "Share your precise location" switch
   - Your exact location becomes visible to the other party
   - You can disable this at any time

4. **View Meeting Point**
   - Click "Show Meeting Point" button
   - See interactive map with:
     - Your location
     - Other party's location (if they're sharing)
     - Suggested meeting point in the middle
   - View distance and address information

### For Lenders/Sellers

1. **Receive Request**
   - Notification appears in your requests dashboard
   - Review request details

2. **Approve Request**
   - Click "Approve" to accept the request
   - OTP system activates for handover verification

3. **Share Location (Optional)**
   - After approval, location sharing section appears
   - Toggle to share your precise location
   - Helps buyer/borrower find you easily

4. **Coordinate Handover**
   - Use meeting point map to arrange meeting
   - Chat with other party using integrated chat
   - Verify handover using OTP system

## Technical Implementation

### Database Fields

#### BorrowRequest Model
```python
lender_shares_location = models.BooleanField(default=False)
borrower_shares_location = models.BooleanField(default=False)
```

#### PurchaseRequest Model
```python
seller_shares_location = models.BooleanField(default=False)
buyer_shares_location = models.BooleanField(default=False)
```

### API Endpoints

#### Toggle Location Sharing
```
POST /products/toggle-location/<request_id>/<request_type>/
```
- Parameters:
  - `request_id`: Integer - ID of borrow or purchase request
  - `request_type`: String - Either 'borrow' or 'purchase'
- Response:
  ```json
  {
    "success": true,
    "shares_location": true,
    "message": "Location sharing enabled"
  }
  ```

#### Get Meeting Point
```
GET /products/meeting-point/<request_id>/<request_type>/
```
- Parameters:
  - `request_id`: Integer - ID of approved request
  - `request_type`: String - Either 'borrow' or 'purchase'
- Response:
  ```json
  {
    "meeting_point": {
      "latitude": 40.7580,
      "longitude": -73.9855,
      "address": "Times Square, Manhattan, NY 10036",
      "distance_km": 2.5
    },
    "user1": {
      "name": "John Doe",
      "latitude": 40.7489,
      "longitude": -73.9680
    },
    "user2": {
      "name": "Jane Smith",
      "latitude": 40.7670,
      "longitude": -74.0030,
      "approximate_location": "Upper West Side, Manhattan",
      "shares_location": true
    }
  }
  ```

### Views Logic

#### `toggle_location_sharing()`
- Validates user is part of the request
- Checks request is approved/active or approved/completed
- Toggles appropriate field based on user role
- Returns JSON response with new state

#### `meeting_point_api()`
- Verifies request is approved
- Checks per-request location sharing flags
- Falls back to global `share_precise_location` setting
- Calculates midpoint using `get_meeting_point()`
- Returns coordinates and addresses

### Frontend Components

#### Alpine.js Component
```javascript
function locationSharing(requestId, requestType, isLender, lenderShares, borrowerShares) {
  return {
    requestId: requestId,
    requestType: requestType,
    sharesLocation: boolean, // Current user's sharing state
    mapLoaded: false,
    meetingInfo: '',
    map: null,
    
    toggleLocation(): async function
    loadMeetingPoint(): async function
  }
}
```

#### UI Elements
1. **Toggle Switch**
   - Tailwind CSS styled
   - Green when enabled, gray when disabled
   - Animated transition

2. **Meeting Point Map**
   - Leaflet.js integration
   - Color-coded markers
   - Auto-fit bounds to show all markers
   - Popup labels for each location

3. **Status Messages**
   - Shows if location sharing is enabled
   - Displays other party's sharing status
   - Distance and address information

## Privacy & Security

### Privacy First Principles

1. **Opt-in Only**
   - No location is shared by default
   - Users must explicitly enable sharing
   - Can be toggled off at any time

2. **Per-Request Basis**
   - Sharing settings are unique to each transaction
   - Enabling for one request doesn't affect others
   - Previous transactions don't automatically share

3. **Approval Required**
   - Location sharing only available after request approval
   - Ensures both parties are committed to the transaction
   - Prevents casual browsing of precise locations

4. **Two-Tier System**
   - Public map: Approximate locations only
   - Approved requests: Option for precise locations
   - Users control which level to use

### Security Measures

1. **Authentication Required**
   - All location endpoints require login
   - `@login_required` decorator on views

2. **Authorization Checks**
   - Users must be part of the request
   - Cannot access other users' location sharing settings
   - Request status validation

3. **CSRF Protection**
   - POST requests require CSRF token
   - Prevents unauthorized location sharing changes

4. **Rate Limiting**
   - Nominatim API: 1 request/second
   - Caching: 24 hours for geocoding, 1 hour for distances
   - Prevents abuse and reduces API load

## User Experience Flow

### Scenario 1: Buy Transaction

1. **Buyer submits purchase request**
   - Sees product with approximate location
   
2. **Seller approves request**
   - Both users now see location sharing section
   - OTP generated for handover verification
   
3. **Seller enables location sharing**
   - Buyer can now see seller's exact address
   - Meeting point updates with precise coordinates
   
4. **Buyer navigates to meeting point**
   - Uses map to find suggested middle ground
   - Confirms meeting via chat
   
5. **Handover completed**
   - OTP verification
   - Transaction marked as completed
   - Location sharing remains active until transaction ends

### Scenario 2: Borrow Transaction

1. **Borrower requests to borrow item**
   - Views approximate location on map
   
2. **Lender approves**
   - Pickup OTP generated
   - Location sharing section appears
   
3. **Both parties share locations**
   - Interactive map shows exact positions
   - Meeting point calculated
   
4. **Pickup with OTP**
   - Borrower shows OTP to lender
   - Item handed over
   - Status changes to "active"
   
5. **Return process**
   - Location sharing still available
   - Return OTP generated
   - Meeting point recalculated if users moved
   
6. **Return completed**
   - Lender verifies return OTP
   - Transaction completed

## Best Practices

### For Users

1. **Enable sharing only when ready**
   - Don't share location until you've arranged a specific meeting time
   - Disable after transaction completes

2. **Use meeting point suggestions**
   - Fair midpoint for both parties
   - Often near public places (safer)

3. **Communicate via chat**
   - Confirm meeting time and location
   - Share updates if running late
   - Coordinate OTP exchange

4. **Verify other party**
   - Check profile information
   - Use OTP system for verification
   - Meet in public places when possible

### For Administrators

1. **Monitor geocoding usage**
   ```bash
   python manage.py geocode_users --all
   ```
   - Run during off-peak hours
   - Respect Nominatim rate limits

2. **Check database indexes**
   ```sql
   EXPLAIN ANALYZE SELECT * FROM registration_user 
   WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
   ```
   - Ensure latitude/longitude index is used

3. **Clear old caches periodically**
   - Distance calculations cache for 1 hour
   - Geocoding results cache for 24 hours
   - Consider implementing cache cleanup

## Troubleshooting

### Location Not Updating

**Problem:** Location sharing toggle doesn't work

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify CSRF token is present in page
3. Ensure request is approved
4. Check user is part of the request

### Meeting Point Not Loading

**Problem:** Map doesn't display or shows error

**Solutions:**
1. Verify both users have geocoded addresses
2. Check Nominatim API is accessible
3. Inspect browser network tab for API errors
4. Ensure Leaflet.js libraries loaded correctly

### Incorrect Meeting Point

**Problem:** Suggested meeting point is far from both users

**Solutions:**
1. Re-geocode user addresses:
   ```bash
   python manage.py geocode_users --all
   ```
2. Check latitude/longitude values in database
3. Verify midpoint calculation logic
4. Consider geographic coordinate system issues (e.g., crossing date line)

## Future Enhancements

### Planned Features

1. **Live Location Tracking**
   - Real-time position updates during active transaction
   - "On my way" status notifications
   - ETA calculations

2. **Custom Meeting Points**
   - Users can set preferred meeting locations
   - Save favorite meeting spots
   - Suggest nearby landmarks

3. **Navigation Integration**
   - Direct links to Google Maps/Apple Maps
   - Turn-by-turn directions
   - Transit options

4. **Location History**
   - View past transaction locations
   - Statistics on travel distances
   - Common meeting areas

5. **Geofencing**
   - Automatic handover prompts when users are nearby
   - Proximity-based notifications
   - Safety check-ins

### Technical Improvements

1. **WebSocket Integration**
   - Real-time location updates
   - Instant map refresh
   - Push notifications

2. **Offline Support**
   - Cached maps for offline viewing
   - Last known location display
   - Queue location updates when back online

3. **Performance Optimization**
   - Spatial database indexes (PostGIS)
   - CDN for map tiles
   - Lazy loading for maps

## Developer Notes

### Adding Location Sharing to New Request Types

1. **Add fields to model**
   ```python
   requester_shares_location = models.BooleanField(default=False)
   provider_shares_location = models.BooleanField(default=False)
   ```

2. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Update views**
   - Add condition to `toggle_location_sharing()`
   - Update `meeting_point_api()` to handle new request type

4. **Add template section**
   - Copy location sharing HTML block
   - Update model field references
   - Adjust Alpine.js initialization

5. **Update URLs**
   ```python
   path('toggle-location/<int:request_id>/<str:request_type>/', 
        views.toggle_location_sharing, 
        name='toggle_location_sharing'),
   ```

### Testing Checklist

- [ ] Location toggle changes database
- [ ] Meeting point API returns correct coordinates
- [ ] Map displays all three markers
- [ ] Privacy: approximate location shown by default
- [ ] Authorization: users can only toggle own requests
- [ ] OTP system still works with new section
- [ ] Mobile responsive design
- [ ] JavaScript errors in console
- [ ] API rate limiting respected
- [ ] Cache working correctly

## Related Documentation

- [Map Feature Guide](MAP_FEATURE_GUIDE.md) - General map feature documentation
- [OTP System Documentation](OTP_SYSTEM_DOCUMENTATION.md) - Handover verification
- [Celery Setup](CELERY_SETUP.md) - Background task processing
- [Chat Integration](OTP_CHAT_INTEGRATION.md) - Communication system

## Support

For issues or questions:
1. Check this documentation first
2. Review error logs in Django admin
3. Test with browser developer tools
4. Check Nominatim API status
5. Verify database migrations applied

---

**Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Active
