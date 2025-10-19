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
            'price',
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
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
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
            'price': 'Price (₹) *',
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
            'price': 'Enter the selling price in Indian Rupees (₹)',
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
        
        # Validate additional images if provided
        for i in range(2, 6):
            image_field = f'image{i}'
            image = cleaned_data.get(image_field)
            
            if image:
                # Check file size
                if image.size > 5 * 1024 * 1024:
                    self.add_error(image_field, 'Image file size must be less than 5MB.')
                
                # Check file type
                if not image.content_type.startswith('image/'):
                    self.add_error(image_field, 'Please upload a valid image file.')
        
        return cleaned_data
