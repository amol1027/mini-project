"""
Script to add sample products across all categories
Run this with: python manage.py shell < add_sample_products.py
or: python add_sample_products.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')
django.setup()

from products.models import Product
from registration.models import User
from decimal import Decimal

# Login credentials
EMAIL = "amolsolse2127@gmail.com"

try:
    # Get the user
    user = User.objects.get(email=EMAIL)
    # Use user ID instead of email to avoid logging PII
    print(f"Found user: User ID {user.id}")
    
    # Sample products data for all categories
    sample_products = [
        # Books Category
        {
            'title': 'Engineering Mathematics Vol 1 by Grewal',
            'description': 'Complete textbook for Engineering Mathematics. Includes solved examples and practice problems. Perfect for first-year engineering students.',
            'category': 'books',
            'condition': 'good',
            'listing_type': 'both',
            'price': Decimal('250.00'),
            'borrow_price_per_day': Decimal('15.00'),
            'borrow_deposit': Decimal('200.00'),
            'max_borrow_days': 30,
        },
        {
            'title': 'Data Structures and Algorithms in Python',
            'description': 'Comprehensive guide to DSA with Python implementations. Includes detailed explanations and code examples.',
            'category': 'books',
            'condition': 'like_new',
            'listing_type': 'sell',
            'price': Decimal('450.00'),
        },
        
        # Notes Category
        {
            'title': 'Operating Systems Complete Notes - Semester 4',
            'description': 'Handwritten notes covering all topics: Process Management, Memory Management, File Systems, and more. Exam-oriented with important questions.',
            'category': 'notes',
            'condition': 'good',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('10.00'),
            'borrow_deposit': Decimal('50.00'),
            'max_borrow_days': 15,
        },
        {
            'title': 'Database Management Systems Notes with SQL Queries',
            'description': 'Complete DBMS notes with SQL query examples, normalization techniques, and ER diagrams. Perfect for exam preparation.',
            'category': 'notes',
            'condition': 'like_new',
            'listing_type': 'both',
            'price': Decimal('100.00'),
            'borrow_price_per_day': Decimal('8.00'),
            'borrow_deposit': Decimal('50.00'),
            'max_borrow_days': 20,
        },
        
        # Electronics Category
        {
            'title': 'Scientific Calculator Casio FX-991EX',
            'description': 'Advanced scientific calculator with 552 functions. Perfect for engineering exams. Includes original box and manual.',
            'category': 'electronics',
            'condition': 'like_new',
            'listing_type': 'sell',
            'price': Decimal('800.00'),
        },
        {
            'title': 'USB Portable Hard Drive 1TB',
            'description': 'Seagate 1TB external hard drive. Great for storing projects, assignments, and study materials. Barely used.',
            'category': 'electronics',
            'condition': 'good',
            'listing_type': 'sell',
            'price': Decimal('2500.00'),
        },
        {
            'title': 'Wireless Mouse Logitech M330',
            'description': 'Silent wireless mouse with long battery life. Perfect for laptop users. Works smoothly.',
            'category': 'electronics',
            'condition': 'good',
            'listing_type': 'both',
            'price': Decimal('600.00'),
            'borrow_price_per_day': Decimal('20.00'),
            'borrow_deposit': Decimal('400.00'),
            'max_borrow_days': 60,
        },
        
        # Stationery Category
        {
            'title': 'Technical Drawing Instruments Box Set',
            'description': 'Complete geometry box with compass, divider, set squares, protractor, and ruler. Essential for engineering drawing.',
            'category': 'stationery',
            'condition': 'good',
            'listing_type': 'sell',
            'price': Decimal('350.00'),
        },
        {
            'title': 'Graph Paper Notebooks - Pack of 3',
            'description': 'Set of 3 graph paper notebooks (100 pages each). Ideal for mathematics, physics, and engineering subjects.',
            'category': 'stationery',
            'condition': 'new',
            'listing_type': 'sell',
            'price': Decimal('150.00'),
        },
        
        # Lab Equipment Category
        {
            'title': 'Digital Multimeter with LCD Display',
            'description': 'Professional digital multimeter for electronics lab. Measures voltage, current, resistance, and continuity. With test leads.',
            'category': 'lab_equipment',
            'condition': 'good',
            'listing_type': 'both',
            'price': Decimal('900.00'),
            'borrow_price_per_day': Decimal('30.00'),
            'borrow_deposit': Decimal('500.00'),
            'max_borrow_days': 30,
        },
        {
            'title': 'Lab Coat - White (Size L)',
            'description': 'Standard white lab coat for chemistry and biology labs. 100% cotton, size Large. Well maintained and clean.',
            'category': 'lab_equipment',
            'condition': 'good',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('5.00'),
            'borrow_deposit': Decimal('100.00'),
            'max_borrow_days': 90,
        },
        
        # Other Category
        {
            'title': 'Student Study Lamp with USB Charging',
            'description': 'LED desk lamp with adjustable brightness and USB charging port. Energy efficient and eye-friendly. Perfect for late-night studies.',
            'category': 'other',
            'condition': 'like_new',
            'listing_type': 'sell',
            'price': Decimal('500.00'),
        },
    ]
    
    # Create products
    created_count = 0
    for product_data in sample_products:
        product_data['seller'] = user
        product_data['is_available'] = True
        
        product = Product.objects.create(**product_data)
        created_count += 1
        print(f"✓ Created: {product.title} (ID: {product.id}) - {product.category}")
    
    print(f"\n{'='*60}")
    print(f"SUCCESS: Created {created_count} products across all categories!")
    print(f"{'='*60}")
    
    # Show category breakdown
    print("\nCategory Breakdown:")
    for category_code, category_name in Product.CATEGORY_CHOICES:
        count = Product.objects.filter(seller=user, category=category_code).count()
        print(f"  {category_name}: {count} products")
    
except User.DoesNotExist:
    print(f"ERROR: User with email '{EMAIL}' not found!")
    print("Please check the credentials and make sure the user exists in the database.")
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
