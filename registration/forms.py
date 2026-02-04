from django import forms
from .models import User
import re
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator

class RegistrationForm(forms.ModelForm):
    """
    Registration form for new users with comprehensive validations
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter password',
            'maxlength': '128',
            'autocomplete': 'new-password'
        }),
        label='Password *',
        min_length=8,
        max_length=128,
        help_text='Password must be at least 8 characters long and contain letters, numbers, and special characters',
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Confirm password',
            'maxlength': '128',
            'autocomplete': 'new-password'
        }),
        label='Confirm Password *',
        max_length=128,
        error_messages={
            'required': 'Please confirm your password.'
        }
    )
    
    class Meta:
        model = User
        fields = ['email', 'name', 'college_id', 'college_name', 'university_name',
                  'address_line1', 'address_line2', 'city', 'state_province', 
                  'zip_postal_code', 'country']
        labels = {
            'email': 'Email Address *',
            'name': 'Full Name *',
            'college_id': 'College ID *',
            'college_name': 'College Name *',
            'university_name': 'University Name *',
            'address_line1': 'Street Address <span class="text-red-600">*</span>',
            'address_line2': 'Apartment, Suite, etc. <span class="text-red-600">*</span>',
            'city': 'City <span class="text-red-600">*</span>',
            'state_province': 'State/Province <span class="text-red-600">*</span>',
            'zip_postal_code': 'ZIP/Postal Code <span class="text-red-600">*</span>',
            'country': 'Country <span class="text-red-600">*</span>',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter your email address',
                'maxlength': '254',
                'autocomplete': 'email'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter your full name',
                'maxlength': '255',
                'autocomplete': 'name',
                'pattern': '[a-zA-Z\s.-]+',
                'title': 'Name can only contain letters, spaces, hyphens, and periods. No numbers allowed.'
            }),
            'college_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter your college ID',
                'maxlength': '50'
            }),
            'college_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter your college name',
                'maxlength': '255',
                'autocomplete': 'organization',
                'pattern': '[a-zA-Z\s.-]+',
                'title': 'College name can only contain letters, spaces, hyphens, and periods. No numbers allowed.'
            }),
            'university_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter your university name',
                'maxlength': '255',
                'pattern': '[a-zA-Z\s.-]+',
                'title': 'University name can only contain letters, spaces, hyphens, and periods. No numbers allowed.'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Street address',
                'maxlength': '255',
                'autocomplete': 'address-line1'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Apartment, suite, etc.',
                'maxlength': '255',
                'autocomplete': 'address-line2'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'City',
                'maxlength': '100',
                'autocomplete': 'address-level2'
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'State/Province',
                'maxlength': '100',
                'autocomplete': 'address-level1'
            }),
            'zip_postal_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'ZIP/Postal code',
                'maxlength': '20',
                'autocomplete': 'postal-code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Country',
                'maxlength': '100',
                'autocomplete': 'country-name'
            }),
        }
    
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        
        if not name:
            raise ValidationError('Name is required.')
        
        # Strip whitespace
        name = name.strip()
        
        # Check minimum length
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        
        # Check maximum length
        if len(name) > 255:
            raise ValidationError('Name is too long. Maximum 255 characters allowed.')
        
        # Check for numerical values
        if re.search(r'\d', name):
            raise ValidationError('Name cannot contain numerical values.')
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z\s.-]+$', name):
            raise ValidationError('Name can only contain letters, spaces, hyphens, and periods.')
        
        # Check for excessive spaces
        if '  ' in name:
            raise ValidationError('Name contains excessive spaces.')
        
        return name
    
    def clean_college_id(self):
        """Validate college ID"""
        college_id = self.cleaned_data.get('college_id')
        
        if not college_id:
            raise ValidationError('College ID is required.')
        
        # Strip whitespace
        college_id = college_id.strip()
        
        # Check length
        if len(college_id) < 3:
            raise ValidationError('College ID must be at least 3 characters long.')
        
        if len(college_id) > 50:
            raise ValidationError('College ID is too long. Maximum 50 characters allowed.')
        
        # Check format (alphanumeric with optional hyphens and underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', college_id):
            raise ValidationError('College ID can only contain letters, numbers, hyphens, and underscores.')
        
        return college_id.upper()  # Normalize to uppercase
    
    def clean_college_name(self):
        """Validate college name"""
        college_name = self.cleaned_data.get('college_name')
        
        if not college_name:
            raise ValidationError('College name is required.')
        
        college_name = college_name.strip()
        
        if len(college_name) < 3:
            raise ValidationError('College name must be at least 3 characters long.')
        
        if len(college_name) > 255:
            raise ValidationError('College name is too long.')

        # Allow digits (e.g., "Institute of Technology 2"), but reject names that are only numeric
        if re.fullmatch(r'[\d\s]+', college_name):
            raise ValidationError('College name cannot be only numbers.')

        # Basic character sanity (letters/numbers/spaces + common punctuation)
        if not re.match(r"^[a-zA-Z0-9\s&.,()'\/-]+$", college_name):
            raise ValidationError("College name contains invalid characters.")
        
        return college_name
    
    def clean_university_name(self):
        """Validate university name"""
        university_name = self.cleaned_data.get('university_name')
        
        if not university_name:
            raise ValidationError('University name is required.')
        
        university_name = university_name.strip()
        
        if len(university_name) < 3:
            raise ValidationError('University name must be at least 3 characters long.')
        
        if len(university_name) > 255:
            raise ValidationError('University name is too long.')

        # Allow digits (e.g., "University of XYZ 2025"), but reject names that are only numeric
        if re.fullmatch(r'[\d\s]+', university_name):
            raise ValidationError('University name cannot be only numbers.')

        # Basic character sanity (letters/numbers/spaces + common punctuation)
        if not re.match(r"^[a-zA-Z0-9\s&.,()'\/-]+$", university_name):
            raise ValidationError("University name contains invalid characters.")
        
        return university_name
    
    def clean_zip_postal_code(self):
        """Validate ZIP/Postal code"""
        zip_code = self.cleaned_data.get('zip_postal_code')
        
        if not zip_code:
            raise ValidationError('ZIP/Postal code is required.')
        
        zip_code = zip_code.strip()
        
        # Check length
        if len(zip_code) > 20:
            raise ValidationError('ZIP/Postal code is too long.')
        
        # Basic format check (alphanumeric with optional spaces and hyphens)
        if not re.match(r'^[a-zA-Z0-9\s-]+$', zip_code):
            raise ValidationError('Invalid ZIP/Postal code format.')
        
        return zip_code
    
    def clean_address_line1(self):
        """Validate address line 1"""
        address_line1 = self.cleaned_data.get('address_line1')
        
        if not address_line1:
            raise ValidationError('Street address is required.')
        
        address_line1 = address_line1.strip()
        
        if len(address_line1) < 3:
            raise ValidationError('Street address must be at least 3 characters long.')
        
        if len(address_line1) > 255:
            raise ValidationError('Street address is too long.')
        
        return address_line1
    
    def clean_address_line2(self):
        """Validate address line 2"""
        address_line2 = self.cleaned_data.get('address_line2')
        
        if not address_line2:
            raise ValidationError('Apartment, suite, etc. is required.')
        
        address_line2 = address_line2.strip()
        
        if len(address_line2) < 1:
            raise ValidationError('This field cannot be empty.')
        
        if len(address_line2) > 255:
            raise ValidationError('This field is too long.')
        
        return address_line2
    
    def clean_city(self):
        """Validate city"""
        city = self.cleaned_data.get('city')
        
        if not city:
            raise ValidationError('City is required.')
        
        city = city.strip()
        
        if len(city) < 2:
            raise ValidationError('City must be at least 2 characters long.')
        
        if len(city) > 100:
            raise ValidationError('City name is too long.')
        
        return city
    
    def clean_state_province(self):
        """Validate state/province"""
        state_province = self.cleaned_data.get('state_province')
        
        if not state_province:
            raise ValidationError('State/Province is required.')
        
        state_province = state_province.strip()
        
        if len(state_province) < 2:
            raise ValidationError('State/Province must be at least 2 characters long.')
        
        if len(state_province) > 100:
            raise ValidationError('State/Province name is too long.')
        
        return state_province
    
    def clean_country(self):
        """Validate country"""
        country = self.cleaned_data.get('country')
        
        if not country:
            raise ValidationError('Country is required.')
        
        country = country.strip()
        
        if len(country) < 2:
            raise ValidationError('Country must be at least 2 characters long.')
        
        if len(country) > 100:
            raise ValidationError('Country name is too long.')
        
        return country
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # Validate password matching
        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match!")
            else:
                # Validate password strength
                if len(password) < 8:
                    self.add_error('password', "Password must be at least 8 characters long.")
                
                if len(password) > 128:
                    self.add_error('password', "Password is too long. Maximum 128 characters allowed.")
                
                # Check for null bytes (security)
                if '\x00' in password:
                    self.add_error('password', "Invalid characters in password.")
                
                # Check for at least one digit
                if not re.search(r'\d', password):
                    self.add_error('password', "Password must contain at least one digit.")
                
                # Check for at least one letter
                if not re.search(r'[A-Za-z]', password):
                    self.add_error('password', "Password must contain at least one letter.")
                
                # Check for at least one special character
                if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/~`]', password):
                    self.add_error('password', "Password must contain at least one special character.")
                
                # Check for uppercase letter
                if not re.search(r'[A-Z]', password):
                    self.add_error('password', "Password must contain at least one uppercase letter.")
                
                # Check for lowercase letter
                if not re.search(r'[a-z]', password):
                    self.add_error('password', "Password must contain at least one lowercase letter.")
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered!")
        
        # Validate email format more strictly
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Please enter a valid email address.")
        
        # Block common disposable email domains
        disposable_domains = [
            'tempmail.com', 'throwaway.email', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'maildrop.cc', 'temp-mail.org', 'fakeinbox.com'
        ]
        email_domain = email.split('@')[1].lower()
        if email_domain in disposable_domains:
            raise forms.ValidationError("Please use a permanent email address, not a disposable one.")
        
        # Validate email length
        if len(email) > 254:  # RFC 5321
            raise forms.ValidationError("Email address is too long.")
        
        local_part, domain = email.rsplit('@', 1)
        if len(local_part) > 64:  # RFC 5321
            raise forms.ValidationError("Email address local part is too long.")
        
        return email.lower()  # Normalize to lowercase
