from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from inventory.models import InventoryRecord, InventoryAlert, ExpirationConfig
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check for expiring and expired inventory items and create alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=None,
            help='Override default check period (days ahead)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        custom_days = options['days_ahead']

        self.stdout.write(
            self.style.SUCCESS(f"Starting expiration check... {'(DRY RUN)' if dry_run else ''}")
        )

        # Get configuration
        config = ExpirationConfig.get_default_config()
        max_days_ahead = custom_days or max(config.alert_thresholds.values())

        # Calculate date range
        today = timezone.now().date()
        check_until = today + timedelta(days=max_days_ahead)

        self.stdout.write(f"Checking expirations from {today} to {check_until}")

        # Get inventory records with expiration dates in range
        expiring_records = InventoryRecord.objects.filter(
            expiration_date__isnull=False,
            expiration_date__gte=today,
            expiration_date__lte=check_until
        ).select_related('product', 'store')

        # Get already expired items
        expired_records = InventoryRecord.objects.filter(
            expiration_date__isnull=False,
            expiration_date__lt=today,
            quantity__gt=0  # Only alert for items still in stock
        ).select_related('product', 'store')

        total_records = len(expiring_records) + len(expired_records)
        self.stdout.write(f"Found {total_records} records to check")

        alerts_created = 0
        alerts_updated = 0

        # Process expired items first
        for record in expired_records:
            days_expired = (today - record.expiration_date).days

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would create EXPIRED alert for {record.product.name} "
                    f"(expired {days_expired} days ago)"
                )
            else:
                alert, created = InventoryAlert.objects.get_or_create(
                    inventory_record=record,
                    alert_type='EXPIRING_SOON',
                    status='ACTIVE',
                    defaults={
                        'priority': 'CRITICAL',
                        'message': f"EXPIRED: {record.product.name} expired on {record.expiration_date} "
                                 f"({days_expired} days ago). Quantity: {record.quantity}",
                        'threshold_value': 0,
                        'current_value': -days_expired,  # Negative to indicate expired
                    }
                )

                if created:
                    alerts_created += 1
                    # Create notifications
                    from inventory.signals import create_notifications_for_alert
                    create_notifications_for_alert(alert, config)
                    self.stdout.write(
                        f"Created EXPIRED alert for {record.product.name}"
                    )
                else:
                    alerts_updated += 1

        # Process expiring items
        for record in expiring_records:
            days_until_expiry = (record.expiration_date - today).days

            # Determine alert priority and threshold
            critical_threshold = config.get_threshold_days('critical')
            warning_threshold = config.get_threshold_days('warning')
            info_threshold = config.get_threshold_days('info')

            if days_until_expiry <= critical_threshold:
                priority = 'CRITICAL'
                threshold_used = critical_threshold
            elif days_until_expiry <= warning_threshold:
                priority = 'HIGH'
                threshold_used = warning_threshold
            elif days_until_expiry <= info_threshold:
                priority = 'MEDIUM'
                threshold_used = info_threshold
            else:
                continue  # No alert needed

            batch_info = f" (Batch: {record.batch_number})" if record.batch_number else ""
            location_info = f" at {record.location}" if record.location else ""

            message = (
                f"Expiring soon: {record.product.name}{batch_info} expires on "
                f"{record.expiration_date} ({days_until_expiry} days remaining){location_info}. "
                f"Quantity: {record.quantity}"
            )

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would create {priority} alert for {record.product.name} "
                    f"({days_until_expiry} days remaining)"
                )
            else:
                alert, created = InventoryAlert.objects.get_or_create(
                    inventory_record=record,
                    alert_type='EXPIRING_SOON',
                    status='ACTIVE',
                    defaults={
                        'priority': priority,
                        'message': message,
                        'threshold_value': threshold_used,
                        'current_value': days_until_expiry,
                    }
                )

                if created:
                    alerts_created += 1
                    # Create notifications
                    from inventory.signals import create_notifications_for_alert
                    create_notifications_for_alert(alert, config)
                    self.stdout.write(
                        f"Created {priority} alert for {record.product.name} "
                        f"({days_until_expiry} days remaining)"
                    )
                else:
                    # Update existing alert if priority changed
                    if alert.priority != priority:
                        alert.priority = priority
                        alert.message = message
                        alert.threshold_value = threshold_used
                        alert.current_value = days_until_expiry
                        alert.save()
                        alerts_updated += 1
                        self.stdout.write(
                            f"Updated alert priority for {record.product.name} to {priority}"
                        )

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN completed. Would create {alerts_created} alerts.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Expiration check completed. Created: {alerts_created}, Updated: {alerts_updated} alerts."
                )
            )

        self.stdout.write("Expiration check finished.")
