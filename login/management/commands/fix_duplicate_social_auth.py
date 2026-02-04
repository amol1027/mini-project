"""
Management command to fix duplicate UserSocialAuth records.
This removes orphaned social auth records that are causing IntegrityErrors.
"""
from django.core.management.base import BaseCommand
from social_django.models import UserSocialAuth
from django.db.models import Count


class Command(BaseCommand):
    help = 'Fix duplicate UserSocialAuth records by removing orphaned entries'

    def handle(self, *args, **options):
        self.stdout.write('Checking for duplicate social auth records...')
        
        # Find duplicates (same provider + uid)
        duplicates = (
            UserSocialAuth.objects
            .values('provider', 'uid')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('✓ No duplicates found'))
            return
        
        self.stdout.write(f'Found {len(duplicates)} duplicate combinations')
        
        fixed = 0
        for dup in duplicates:
            provider = dup['provider']
            uid = dup['uid']
            
            # Get all records with this provider+uid
            records = UserSocialAuth.objects.filter(
                provider=provider,
                uid=uid
            ).order_by('created')  # Keep the oldest one
            
            if records.count() > 1:
                # Keep the first (oldest) record, delete the rest
                first_record = records.first()
                duplicates_to_delete = records.exclude(id=first_record.id)
                
                count = duplicates_to_delete.count()
                self.stdout.write(
                    f'Removing {count} duplicate(s) for {provider}:{uid} '
                    f'(keeping record for user: {first_record.user})'
                )
                
                duplicates_to_delete.delete()
                fixed += count
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Fixed {fixed} duplicate social auth records')
        )
