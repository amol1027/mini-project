"""
Script to populate the database with 15-20 diverse products for testing
"""

import os
import sys
import django
from decimal import Decimal

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')
django.setup()

from registration.models import User
from products.models import Product

def create_or_get_user():
    """
    Create or retrieve a test user for populating products.
    Note: This creates a regular user without admin privileges.
    To create admin users, use Django's createsuperuser command or admin UI.
    """
    email = "testuser@example.com"
    password = "testpass123"
    
    try:
        user = User.objects.get(email=email)
        print(f"✓ User found: {user.email}")
        return user
    except User.DoesNotExist:
        print(f"Creating new test user: {email}")
        user = User.objects.create(
            email=email,
            college_id="TEST001",
            name="Test User",
            college_name="Test Engineering College",
            university_name="Test University",
            email_verified=True,
            is_admin=False,  # Never grant admin privileges via populate scripts
            city="Mumbai",
            state_province="Maharashtra",
            country="India"
        )
        user.set_password(password)
        user.save()
        print(f"✓ Test user created: {user.email}")
        print(f"  Login credentials: {email} / {password}")
        print(f"  Note: This is a regular user. For admin access, use Django's createsuperuser command.")
        return user

def create_products(seller):
    """Create 20 diverse educational products"""
    
    products_data = [
        {
            'title': 'Introduction to Algorithms (CLRS) 3rd Edition',
            'description': 'Comprehensive textbook covering fundamental algorithms. Perfect condition with minimal highlighting. All chapters intact.',
            'category': 'books',
            'condition': 'like_new',
            'listing_type': 'both',
            'price': Decimal('850.00'),
            'borrow_price_per_day': Decimal('30.00'),
            'borrow_deposit': Decimal('500.00'),
            'max_borrow_days': 15
        },
        {
            'title': 'Scientific Calculator Casio FX-991ES Plus',
            'description': 'Advanced scientific calculator with 417 functions. Perfect for engineering students. Battery included.',
            'category': 'electronics',
            'condition': 'good',
            'listing_type': 'sell',
            'price': Decimal('650.00'),
        },
        {
            'title': 'Data Structures Complete Notes - Semester 3',
            'description': 'Comprehensive handwritten notes covering all topics: Trees, Graphs, Hashing, Sorting algorithms. University exam oriented.',
            'category': 'notes',
            'condition': 'new',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('15.00'),
            'borrow_deposit': Decimal('100.00'),
            'max_borrow_days': 10
        },
        {
            'title': 'Engineering Drawing Instruments Set',
            'description': 'Complete geometry box with compass, divider, protractor, and scales. Brand: Camlin. Barely used.',
            'category': 'stationery',
            'condition': 'like_new',
            'listing_type': 'sell',
            'price': Decimal('450.00'),
        },
        {
            'title': 'Digital Multimeter UNI-T UT33D',
            'description': 'Pocket-size digital multimeter for electronics lab. Measures voltage, current, resistance. Includes test leads.',
            'category': 'lab_equipment',
            'condition': 'good',
            'listing_type': 'both',
            'price': Decimal('550.00'),
            'borrow_price_per_day': Decimal('25.00'),
            'borrow_deposit': Decimal('300.00'),
            'max_borrow_days': 7
        },
        {
            'title': 'Database Management Systems by Ramakrishnan',
            'description': 'Standard textbook for DBMS course. Covers SQL, normalization, transactions, query processing. Good condition.',
            'category': 'books',
            'condition': 'good',
            'listing_type': 'both',
            'price': Decimal('700.00'),
            'borrow_price_per_day': Decimal('25.00'),
            'borrow_deposit': Decimal('400.00'),
            'max_borrow_days': 20
        },
        {
            'title': 'Arduino Uno R3 Development Board',
            'description': 'Original Arduino Uno R3 with USB cable. Perfect for IoT and embedded systems projects. Tested working.',
            'category': 'electronics',
            'condition': 'good',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('40.00'),
            'borrow_deposit': Decimal('800.00'),
            'max_borrow_days': 14
        },
        {
            'title': 'Operating Systems Notes - Complete Module',
            'description': 'Detailed notes on Process Management, Memory Management, File Systems, Deadlocks. Includes diagrams and examples.',
            'category': 'notes',
            'condition': 'new',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('20.00'),
            'borrow_deposit': Decimal('150.00'),
            'max_borrow_days': 10
        },
        {
            'title': 'Staedtler Technical Drawing Pens Set',
            'description': 'Set of 4 technical pens (0.3, 0.5, 0.7, 1.0mm). Ideal for engineering drawings. Barely used.',
            'category': 'stationery',
            'condition': 'like_new',
            'listing_type': 'sell',
            'price': Decimal('380.00'),
        },
        {
            'title': 'Breadboard 830 Points with Jumper Wires',
            'description': 'Solderless breadboard for circuit prototyping. Includes 65pcs jumper wire kit. Essential for electronics lab.',
            'category': 'lab_equipment',
            'condition': 'new',
            'listing_type': 'sell',
            'price': Decimal('250.00'),
        },
        {
            'title': 'Computer Networks by Tanenbaum 5th Edition',
            'description': 'Comprehensive guide to computer networking. Covers protocols, layered architecture, security. Excellent condition.',
            'category': 'books',
            'condition': 'like_new',
            'listing_type': 'both',
            'price': Decimal('750.00'),
            'borrow_price_per_day': Decimal('28.00'),
            'borrow_deposit': Decimal('450.00'),
            'max_borrow_days': 15
        },
        {
            'title': 'TI-84 Plus Graphing Calculator',
            'description': 'Advanced graphing calculator for calculus and statistics. Preloaded with exam-approved software.',
            'category': 'electronics',
            'condition': 'good',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('50.00'),
            'borrow_deposit': Decimal('1500.00'),
            'max_borrow_days': 10
        },
        {
            'title': 'Machine Learning Complete Study Material',
            'description': 'Comprehensive notes and solved problems on ML algorithms, neural networks, deep learning. Great for exams.',
            'category': 'notes',
            'condition': 'new',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('25.00'),
            'borrow_deposit': Decimal('200.00'),
            'max_borrow_days': 12
        },
        {
            'title': 'A4 Engineering Paper Pad - 100 Sheets',
            'description': 'Premium quality engineering paper pad. Grid lines for technical drawings. Unopened pack.',
            'category': 'stationery',
            'condition': 'new',
            'listing_type': 'sell',
            'price': Decimal('150.00'),
        },
        {
            'title': 'Digital Oscilloscope DSO138',
            'description': 'Pocket-sized digital oscilloscope kit. Perfect for signal analysis in electronics projects.',
            'category': 'lab_equipment',
            'condition': 'good',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('60.00'),
            'borrow_deposit': Decimal('1200.00'),
            'max_borrow_days': 7
        },
        {
            'title': 'Python Programming - From Beginner to Advanced',
            'description': 'Complete Python programming guide with examples. Covers basics to advanced OOP and frameworks.',
            'category': 'books',
            'condition': 'good',
            'listing_type': 'both',
            'price': Decimal('600.00'),
            'borrow_price_per_day': Decimal('22.00'),
            'borrow_deposit': Decimal('350.00'),
            'max_borrow_days': 20
        },
        {
            'title': 'Raspberry Pi 4 Model B - 4GB RAM',
            'description': 'Single board computer for IoT, robotics, and computing projects. Includes power adapter and SD card.',
            'category': 'electronics',
            'condition': 'like_new',
            'listing_type': 'sell',
            'price': Decimal('4500.00'),
        },
        {
            'title': 'Compiler Design Notes with Example Programs',
            'description': 'Detailed notes on lexical analysis, parsing, code generation. Includes example programs and diagrams.',
            'category': 'notes',
            'condition': 'new',
            'listing_type': 'lend',
            'borrow_price_per_day': Decimal('18.00'),
            'borrow_deposit': Decimal('120.00'),
            'max_borrow_days': 10
        },
        {
            'title': 'Faber-Castell Mechanical Pencil Set',
            'description': 'Professional mechanical pencil set with 0.5mm and 0.7mm leads. Includes eraser refills.',
            'category': 'stationery',
            'condition': 'new',
            'listing_type': 'sell',
            'price': Decimal('280.00'),
        },
        {
            'title': 'Logic Analyzer 8 Channel USB',
            'description': '8-channel USB logic analyzer for debugging digital circuits. Compatible with Sigrok/PulseView software.',
            'category': 'lab_equipment',
            'condition': 'good',
            'listing_type': 'both',
            'price': Decimal('850.00'),
            'borrow_price_per_day': Decimal('45.00'),
            'borrow_deposit': Decimal('500.00'),
            'max_borrow_days': 7
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    print("\nCreating products...")
    print("=" * 80)
    
    for product_data in products_data:
        # Check if product already exists
        existing = Product.objects.filter(
            title=product_data['title'],
            seller=seller
        ).first()
        
        if existing:
            print(f"⊗ Skipped (already exists): {product_data['title']}")
            skipped_count += 1
            continue
        
        # Create the product
        product = Product.objects.create(
            seller=seller,
            **product_data
        )
        created_count += 1
        listing_type_display = dict(Product.LISTING_TYPE_CHOICES)[product.listing_type]
        print(f"✓ Created: {product.title[:60]} [{listing_type_display}]")
    
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  Created: {created_count} products")
    print(f"  Skipped: {skipped_count} products (already exist)")
    print(f"  Total: {created_count + skipped_count} products processed")
    print(f"\n✓ Script completed successfully!")

def main():
    """Main function to run the script"""
    print("Product Population Script")
    print("=" * 80)
    
    # Create or get user
    seller = create_or_get_user()
    
    # Create products
    create_products(seller)

if __name__ == '__main__':
    main()
