from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from authentication.models import PasswordResetToken


class Command(BaseCommand):
    help = 'Clean up expired password reset tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete tokens older than this many days (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find expired tokens
        expired_tokens = PasswordResetToken.objects.filter(
            created_at__lt=cutoff_date
        )
        
        count = expired_tokens.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} password reset tokens older than {days} days'
                )
            )
            for token in expired_tokens[:10]:  # Show first 10 examples
                self.stdout.write(f'  - Token for {token.user.username} created on {token.created_at}')
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            if count > 0:
                expired_tokens.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted {count} expired password reset tokens'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('No expired tokens found to delete')
                ) 