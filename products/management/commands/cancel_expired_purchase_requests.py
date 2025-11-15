"""
Management command to cancel expired purchase requests
Run this periodically (e.g., via cron job or Celery beat)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import DatabaseError
from django.core.exceptions import ValidationError
from products.models import PurchaseRequest


class Command(BaseCommand):
    help = 'Cancel purchase requests that have been approved but not completed within 24 hours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cancelled without actually cancelling',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all approved requests that are expired
        approved_requests = PurchaseRequest.objects.filter(
            status='approved',
            handover_otp_verified=False
        ).select_related('product', 'buyer', 'seller')
        
        expired_count = 0
        cancelled_count = 0
        failed_count = 0
        
        for request in approved_requests:
            if request.is_expired():
                expired_count += 1
                
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Would cancel: Purchase Request #{request.id} - '
                            f'{request.product.title} (approved {request.approved_date})'
                        )
                    )
                else:
                    # Cancel the request
                    try:
                        request.status = 'cancelled'
                        existing_response = request.seller_response if request.seller_response else ""
                        request.seller_response = (
                            f"{existing_response}\n\n"
                            "Auto-cancelled: Handover not completed within 24 hours of approval."
                        ).strip()
                        request.save()
                        
                        cancelled_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Cancelled: Purchase Request #{request.id} - {request.product.title}'
                            )
                        )
                    except (ValidationError, DatabaseError) as e:
                        failed_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'Failed to cancel Purchase Request #{request.id} - {request.product.title}: '
                                f'{type(e).__name__}: {str(e)}'
                            )
                        )
                        # Continue processing remaining requests
                        continue
                    except Exception as e:
                        failed_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'Unexpected error cancelling Purchase Request #{request.id} - '
                                f'{request.product.title}: {type(e).__name__}: {str(e)}'
                            )
                        )
                        # Continue processing remaining requests
                        continue
        
        if expired_count == 0:
            self.stdout.write(self.style.SUCCESS('No expired purchase requests found.'))
        else:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nFound {expired_count} expired request(s). '
                        f'Run without --dry-run to cancel them.'
                    )
                )
            else:
                summary = f'\nSuccessfully cancelled {cancelled_count} of {expired_count} expired purchase request(s).'
                if failed_count > 0:
                    summary += f' {failed_count} request(s) failed to cancel.'
                    self.stdout.write(self.style.WARNING(summary))
                else:
                    self.stdout.write(self.style.SUCCESS(summary))
