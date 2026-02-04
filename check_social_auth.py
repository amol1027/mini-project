import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')
django.setup()

from social_django.models import UserSocialAuth

print(f'Total UserSocialAuth records: {UserSocialAuth.objects.count()}')
print('\nExisting social auth records:')
for usa in UserSocialAuth.objects.all():
    print(f'  - Provider: {usa.provider}, UID: {usa.uid}, User: {usa.user.username} (ID: {usa.user.id})')
