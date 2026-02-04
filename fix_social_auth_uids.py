"""
Fix UserSocialAuth records that have email as UID instead of numeric Google ID.
This script will delete invalid records so they can be recreated properly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')
django.setup()

from social_django.models import UserSocialAuth

print('Checking for UserSocialAuth records with email as UID...\n')

# Find records where UID looks like an email (contains @)
invalid_records = UserSocialAuth.objects.filter(provider='google-oauth2', uid__contains='@')

if invalid_records.exists():
    print(f'Found {invalid_records.count()} invalid record(s):')
    for record in invalid_records:
        print(f'  - UID: {record.uid}, User: {record.user.username}')
    
    print('\nThese records have email as UID instead of numeric Google ID.')
    print('They will be deleted and recreated on next login.\n')
    
    confirm = input('Delete these records? (yes/no): ')
    if confirm.lower() == 'yes':
        count = invalid_records.count()
        invalid_records.delete()
        print(f'\n✓ Deleted {count} invalid record(s).')
        print('Users can now log in again with Google OAuth.')
    else:
        print('\nCancelled. No changes made.')
else:
    print('✓ No invalid records found. All UIDs are properly formatted.')
