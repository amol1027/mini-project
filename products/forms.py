from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    """
    Form for creating and editing products
    """
    
    class Meta:
        model = Product
        fields = [
            'title', 
            'description', 
            'category', 
            'condition',
            'listing_type',
            'price',
            'borrow_price_per_day',
            'borrow_deposit',
            'max_borrow_days',
            'image1',
            'image2',
            'image3',
            'image4',
            'image5',
            'is_available'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Enter product title (e.g., "Data Structures Textbook")',
                'maxlength': '255'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Describe your product in detail (condition, features, reason for selling, etc.)',
                'rows': 5
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'condition': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'listing_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'borrow_price_per_day': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'borrow_deposit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'max_borrow_days': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': '30',
                'min': '1'
            }),
            'image1': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'image1'
            }),
            'image2': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'image2'
            }),
            'image3': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'image3'
            }),
            'image4': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'image4'
            }),
            'image5': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'image5'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            })
        }
        
        labels = {
            'title': 'Product Title *',
            'description': 'Description *',
            'category': 'Category *',
            'condition': 'Condition *',
            'listing_type': 'Listing Type *',
            'price': 'Sale Price (₹)',
            'borrow_price_per_day': 'Borrow Price Per Day (₹)',
            'borrow_deposit': 'Security Deposit (₹)',
            'max_borrow_days': 'Maximum Borrow Days',
            'image1': 'Primary Image *',
            'image2': 'Additional Image (Optional)',
            'image3': 'Additional Image (Optional)',
            'image4': 'Additional Image (Optional)',
            'image5': 'Additional Image (Optional)',
            'is_available': 'Mark as Available'
        }
        
        help_texts = {
            'title': 'Enter a clear, descriptive title for your product',
            'description': 'Provide detailed information about the product',
            'listing_type': 'Choose whether to sell, lend, or both',
            'price': 'Enter the selling price (required for "For Sale" or "Both")',
            'borrow_price_per_day': 'Daily rental rate (required for "For Lending" or "Both")',
            'borrow_deposit': 'Refundable security deposit amount',
            'max_borrow_days': 'Maximum duration the item can be borrowed',
            'image1': 'Upload the main product image (JPG, PNG, max 5MB)',
            'is_available': 'Uncheck this if the product is no longer available'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make image1 required
        self.fields['image1'].required = True
        
        # Set default for is_available to True
        if not self.instance.pk:
            self.initial['is_available'] = True
    
    def clean_price(self):
        """Validate that price is positive"""
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('Price must be greater than zero.')
        return price
    
    def clean_image1(self):
        """Validate primary image"""
        image = self.cleaned_data.get('image1')
        
        if image:
            # Only validate if it's a newly uploaded file (has content_type attribute)
            if hasattr(image, 'content_type'):
                # Check file size (max 5MB)
                if image.size > 5 * 1024 * 1024:
                    raise forms.ValidationError('Image file size must be less than 5MB.')
                
                # Check file type
                if not image.content_type.startswith('image/'):
                    raise forms.ValidationError('Please upload a valid image file.')
        
        return image
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        listing_type = cleaned_data.get('listing_type')
        price = cleaned_data.get('price')
        borrow_price = cleaned_data.get('borrow_price_per_day')
        
        # Validate pricing based on listing type
        if listing_type in ['sell', 'both']:
            if not price or price <= 0:
                self.add_error('price', 'Sale price is required for items listed for sale.')
        
        if listing_type in ['lend', 'both']:
            if not borrow_price or borrow_price <= 0:
                self.add_error('borrow_price_per_day', 'Daily rental price is required for items available for lending.')
        
        # Validate additional images if provided (only newly uploaded files)
        for i in range(2, 6):
            image_field = f'image{i}'
            image = cleaned_data.get(image_field)
            
            if image and hasattr(image, 'content_type'):
                # Only validate newly uploaded files
                # Check file size
                if image.size > 5 * 1024 * 1024:
                    self.add_error(image_field, 'Image file size must be less than 5MB.')
                
                # Check file type
                if not image.content_type.startswith('image/'):
                    self.add_error(image_field, 'Please upload a valid image file.')
        
        return cleaned_data


class BorrowRequestForm(forms.Form):
    """
    Form for creating a borrow request
    """
    requested_days = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'placeholder': 'Number of days',
            'min': '1'
        }),
        label='Number of Days',
        help_text='How many days do you need to borrow this item?'
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'placeholder': 'Add a message to the lender (optional)',
            'rows': 3
        }),
        label='Message (Optional)',
        help_text='Introduce yourself and explain why you need this item'
    )
    
    def __init__(self, *args, max_days=None, **kwargs):
        super().__init__(*args, **kwargs)
        if max_days:
            self.fields['requested_days'].max_value = max_days
            self.fields['requested_days'].widget.attrs['max'] = max_days
            self.fields['requested_days'].help_text = f'How many days do you need to borrow this item? (Max: {max_days} days)'
