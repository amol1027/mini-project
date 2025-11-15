from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator, MaxValueValidator

class User(models.Model):
    """
    Custom User model for Student Resource Exchange
    """
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, db_index=True, max_length=255)
    password_hash = models.CharField(max_length=128)
    college_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255, blank=True, null=True)
    college_name = models.CharField(max_length=255, blank=True, null=True)
    university_name = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(default=0)
    email_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    # Address fields
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    zip_postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Geolocation fields
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude coordinate"
    )
    share_precise_location = models.BooleanField(
        default=False,
        help_text="Share exact location with approved requesters"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password is correct"""
        return check_password(raw_password, self.password_hash)
    
    def get_full_address(self):
        """Return full address as string"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state_province,
            self.zip_postal_code,
            self.country
        ]
        return ', '.join(filter(None, parts))
    
    def get_approximate_location(self):
        """Return city-level location for privacy"""
        parts = [self.city, self.state_province, self.country]
        return ', '.join(filter(None, parts))
    
    def has_location(self):
        """Check if user has valid coordinates"""
        return self.latitude is not None and self.longitude is not None
