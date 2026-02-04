from django import forms
from registration.models import User
import re
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    """
    Login form for user authentication with comprehensive validations
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'placeholder': 'Enter your email address',
            'maxlength': '254',
            'autocomplete': 'email'
        }),
        label='Email Address',
        max_length=254,
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'placeholder': 'Enter your password',
            'maxlength': '128',
            'autocomplete': 'current-password'
        }),
        label='Password',
        min_length=8,
        max_length=128,
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        }),
        label='Remember me'
    )
    
    def clean_email(self):
        """Validate and sanitize email address"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email address is required.')
        
        # Strip whitespace and normalize to lowercase
        email = email.strip().lower()
        
        # Validate email format more strictly
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('Please enter a valid email address.')
        
        # Validate email length
        if len(email) > 254:  # RFC 5321
            raise ValidationError('Email address is too long.')
        
        # Validate local part and domain lengths
        try:
            local_part, domain = email.rsplit('@', 1)
            if len(local_part) > 64:  # RFC 5321
                raise ValidationError('Email address local part is too long.')
            if len(domain) > 253:
                raise ValidationError('Email domain is too long.')
        except ValueError:
            raise ValidationError('Invalid email format.')
        
        return email
    
    def clean_password(self):
        """Validate password"""
        password = self.cleaned_data.get('password')
        
        if not password:
            raise ValidationError('Password is required.')
        
        # Check minimum length
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        # Check maximum length
        if len(password) > 128:
            raise ValidationError('Password is too long. Maximum 128 characters allowed.')
        
        # Check for null bytes (security)
        if '\x00' in password:
            raise ValidationError('Invalid characters in password.')
        
        return password
    
    def clean(self):
        """Additional form-wide validation"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        # Ensure both fields are present
        if not email or not password:
            if not email:
                self.add_error('email', 'Email address is required.')
            if not password:
                self.add_error('password', 'Password is required.')
        
        return cleaned_data
