from django.core.management.base import BaseCommand
from products.models import Product
from registration.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create 10 sample products for the Student Resource Exchange'

    def handle(self, *args, **kwargs):
        # Get or create a sample seller (use first user or create one)
        seller = User.objects.first()
        
        if not seller:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
        
        # Delete existing products to avoid duplicates
        Product.objects.all().delete()
        
        sample_products = [
            {
                'title': 'Engineering Mathematics Textbook - 3rd Edition',
                'description': 'Complete engineering mathematics textbook covering calculus, linear algebra, differential equations, and probability. Perfect condition with minimal highlighting. All chapters intact with practice problems and solutions.',
                'category': 'books',
                'condition': 'like_new',
                'price': Decimal('450.00'),
            },
            {
                'title': 'Complete Data Structures Notes (Handwritten)',
                'description': 'Comprehensive handwritten notes for Data Structures course including arrays, linked lists, trees, graphs, sorting algorithms, and dynamic programming. Clear diagrams and examples included.',
                'category': 'notes',
                'condition': 'good',
                'price': Decimal('200.00'),
            },
            {
                'title': 'Scientific Calculator (Casio FX-991EX)',
                'description': 'Advanced scientific calculator with 552 functions, natural display, and spreadsheet capabilities. Barely used, includes original box and manual. Perfect for engineering students.',
                'category': 'electronics',
                'condition': 'like_new',
                'price': Decimal('1200.00'),
            },
            {
                'title': 'Premium Stationery Bundle',
                'description': 'Complete stationery set including gel pens (10 colors), highlighters, sticky notes, notebooks (5 pieces), and a pencil case. Perfect for new semester. Brand new and unused.',
                'category': 'stationery',
                'condition': 'new',
                'price': Decimal('350.00'),
            },
            {
                'title': 'Physics Lab Equipment Set',
                'description': 'Basic physics lab equipment including vernier caliper, micrometer screw gauge, spring balance, and measuring tape. Good working condition, recently calibrated.',
                'category': 'lab_equipment',
                'condition': 'good',
                'price': Decimal('800.00'),
            },
            {
                'title': 'Programming in C++ by Balagurusamy',
                'description': 'Complete C++ programming textbook with object-oriented concepts. Includes CD with source code examples. Minor wear on cover but all pages intact. Great for beginners.',
                'category': 'books',
                'condition': 'good',
                'price': Decimal('350.00'),
            },
            {
                'title': 'Operating Systems Complete Notes',
                'description': 'Detailed notes covering process management, memory management, file systems, and scheduling algorithms. Includes diagrams and real-world examples. University exam focused.',
                'category': 'notes',
                'condition': 'like_new',
                'price': Decimal('250.00'),
            },
            {
                'title': 'Wireless Mouse and Keyboard Combo',
                'description': 'Logitech wireless keyboard and mouse combo with USB receiver. Ergonomic design, long battery life. Excellent condition with minimal usage. Perfect for laptop users.',
                'category': 'electronics',
                'condition': 'like_new',
                'price': Decimal('1500.00'),
            },
            {
                'title': 'Graph Paper Notebook (Pack of 3)',
                'description': 'Set of 3 graph paper notebooks (100 pages each) with 5mm grid. Ideal for engineering drawing, math problems, and circuit diagrams. Brand new, never used.',
                'category': 'stationery',
                'condition': 'new',
                'price': Decimal('150.00'),
            },
            {
                'title': 'Digital Multimeter with Probes',
                'description': 'Professional digital multimeter for measuring voltage, current, resistance, and continuity. Includes test probes and carrying case. Essential for electronics lab work.',
                'category': 'lab_equipment',
                'condition': 'good',
                'price': Decimal('650.00'),
            },
        ]
        
        created_count = 0
        for product_data in sample_products:
            product = Product.objects.create(
                seller=seller,
                **product_data
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created product: {product.title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} sample products!')
        )
