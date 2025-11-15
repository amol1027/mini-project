"""
Management command to geocode existing users
Usage: python manage.py geocode_users

Security Note: This command uses user IDs instead of email addresses in logs
to avoid exposing PII (Personally Identifiable Information) in command output
and log files. All logging follows GDPR and privacy best practices.
"""
from django.core.management.base import BaseCommand
from registration.models import User
from registration.geocoding_utils import geocode_user
import time

class Command(BaseCommand):
    help = 'Geocode addresses for all users who have addresses but no coordinates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Geocode all users (including those with existing coordinates)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of users to process',
        )

    def handle(self, *args, **options):
        # Get users without coordinates
        if options['all']:
            users = User.objects.exclude(
                city__isnull=True
            ).exclude(
                city=''
            )
            self.stdout.write("Geocoding ALL users with addresses...")
        else:
            users = User.objects.filter(
                latitude__isnull=True
            ).exclude(
                city__isnull=True
            ).exclude(
                city=''
            )
            self.stdout.write("Geocoding users without coordinates...")
        
        # Apply limit and get actual count
        if options['limit']:
            users = list(users[:options['limit']])
            total = len(users)
        else:
            total = users.count()
        
        self.stdout.write(f"Found {total} users to geocode")
        
        success_count = 0
        fail_count = 0
        
        for i, user in enumerate(users, 1):
            # Use user ID instead of email to avoid logging PII
            self.stdout.write(f"Processing {i}/{total}: User ID {user.id}")
            
            try:
                if geocode_user(user):
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Success: ({user.latitude}, {user.longitude})"
                        )
                    )
                else:
                    fail_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Failed to geocode User ID {user.id}")
                    )
            except Exception as e:
                fail_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Exception geocoding User ID {user.id}: {type(e).__name__}: {str(e)}"
                    )
                )
            
            # Rate limiting: 1 request per second
            if i < total:
                time.sleep(1)
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Geocoding complete: {success_count} successful, {fail_count} failed"
            )
        )
