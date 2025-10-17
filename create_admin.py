"""
Script to create the hardcoded admin user
Run this with: python create_admin.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')
django.setup()

from registration.models import User

# Admin credentials
ADMIN_EMAIL = "amolsolse2127@gmail.com"
ADMIN_PASSWORD = "amolsolse2127@gmail.com"

# Check if admin already exists
admin_user = User.objects.filter(email=ADMIN_EMAIL).first()

if admin_user:
    # Update existing user to be admin
    admin_user.is_admin = True
    admin_user.set_password(ADMIN_PASSWORD)
    admin_user.email_verified = True
    admin_user.name = "Admin"
    admin_user.college_id = "ADMIN001"
    admin_user.save()
    print(f"✅ Updated existing user '{ADMIN_EMAIL}' to admin status")
else:
    # Create new admin user
    admin_user = User(
        email=ADMIN_EMAIL,
        college_id="ADMIN001",
        name="Admin",
        email_verified=True,
        is_admin=True
    )
    admin_user.set_password(ADMIN_PASSWORD)
    admin_user.save()
    print(f"✅ Created new admin user: {ADMIN_EMAIL}")

print(f"\n📧 Email: {ADMIN_EMAIL}")
print(f"🔑 Password: {ADMIN_PASSWORD}")
print(f"👑 Admin Status: {admin_user.is_admin}")
