from django.core.management.base import BaseCommand
from django.utils import timezone
from user.models import OTP


class Command(BaseCommand):
    help = "Clean up expired OTPs from the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        
        # Find expired OTPs
        expired_otps = OTP.objects.filter(expires_at__lt=timezone.now())
        count = expired_otps.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would delete {count} expired OTPs")
            )
            if count > 0:
                self.stdout.write("Expired OTPs that would be deleted:")
                for otp in expired_otps[:10]:  # Show first 10
                    self.stdout.write(f"  - {otp.email}: {otp.otp_code} (expired: {otp.expires_at})")
                if count > 10:
                    self.stdout.write(f"  ... and {count - 10} more")
        else:
            deleted_count, _ = expired_otps.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {deleted_count} expired OTPs")
            ) 