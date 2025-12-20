"""
Script to create a Django superuser for admin panel access
"""

import os
import sys
import django

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Create or update Django superuser for admin panel"""
    username = "admin"
    email = "admin@sre.com"
    password = "admin123"
    
    try:
        # Check if superuser already exists
        user = User.objects.get(username=username)
        print(f"✓ Superuser '{username}' already exists")
        
        # Update password
        user.set_password(password)
        user.save()
        print(f"✓ Password updated for '{username}'")
        
    except User.DoesNotExist:
        # Create new superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ Superuser created: {username}")
    
    print("\n" + "=" * 60)
    print("Django Admin Credentials:")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Admin URL: http://localhost:8000/admin/")
    print("=" * 60)

if __name__ == '__main__':
    create_superuser()
