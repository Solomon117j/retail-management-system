"""
Management command to process predictive replenishment for all products
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.replenishment_utils import BulkReplenishmentProcessor
from inventory.models import ReplenishmentBatch
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process predictive replenishment for all products and create bulk orders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--store-id',
            type=int,
            help='Process replenishment for specific warehouse only (must be warehouse type)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating orders',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force processing even if recent batch exists',
        )

    def handle(self, *args, **options):
        store_id = options.get('store_id')
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        self.stdout.write(
            self.style.SUCCESS(f"Starting replenishment processing{' (DRY RUN)' if dry_run else ''}")
        )

        # Check for recent batches if not forced
        if not force:
            recent_batch = ReplenishmentBatch.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=1),
                status__in=['PENDING', 'COMPLETED']
            ).first()

            if recent_batch:
                self.stdout.write(
                    self.style.WARNING(
                        f"Recent replenishment batch found ({recent_batch.created_at}). "
                        "Use --force to override."
                    )
                )
                return

        # Initialize processor
        if store_id:
            from store_management.models import Store
            try:
                store = Store.objects.get(id=store_id)
                if store.store_type != 'warehouse':
                    self.stdout.write(
                        self.style.ERROR(f"Store {store.name} is not a warehouse. Only warehouses can place orders to suppliers.")
                    )
                    return
            except Store.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Store with ID {store_id} does not exist.")
                )
                return

        processor = BulkReplenishmentProcessor(store)

        # Get products needing reorder
        products_needing_reorder = processor.get_products_needing_reorder()

        if not products_needing_reorder:
            self.stdout.write(
                self.style.SUCCESS("No products currently need replenishment")
            )
            return

        self.stdout.write(
            f"Found {len(products_needing_reorder)} products needing replenishment"
        )

        # Group by supplier
        supplier_groups = processor.group_by_supplier(products_needing_reorder)

        if dry_run:
            self._show_dry_run_summary(supplier_groups)
            return

        # Create bulk orders
        orders_created = processor.create_bulk_orders(supplier_groups)

        # Report results
        self._show_results(orders_created)

    def _show_dry_run_summary(self, supplier_groups):
        """Show what would be done in a dry run"""
        self.stdout.write("\nDRY RUN SUMMARY:")
        self.stdout.write("=" * 50)

        total_products = 0
        total_value = 0

        for supplier, products in supplier_groups.items():
            self.stdout.write(f"\nSupplier: {supplier.name}")
            supplier_value = 0

            for data in products:
                product = data['product']
                quantity = data['optimal_order_quantity']
                supplier_product = data['supplier_product']

                if supplier_product:
                    value = quantity * supplier_product.supply_price
                    supplier_value += value
                    total_value += value

                    self.stdout.write(
                        f"  - {product.name}: {quantity} units @ ${supplier_product.supply_price:.2f} = ${value:.2f}"
                    )

            self.stdout.write(f"  Supplier Total: ${supplier_value:.2f}")
            total_products += len(products)

        self.stdout.write(f"\nTOTAL: {total_products} products, ${total_value:.2f} value")

    def _show_results(self, orders_created):
        """Show results of actual processing"""
        if not orders_created:
            self.stdout.write(
                self.style.WARNING("No orders were created")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully created {len(orders_created)} replenishment batches:")
        )

        total_value = 0
        total_products = 0

        for order_data in orders_created:
            batch = order_data['batch']
            po = order_data['purchase_order']
            items_count = order_data['items_count']
            value = order_data['total_value']

            total_value += value
            total_products += items_count

            status_display = "AUTO-APPROVED" if po.status == 'auto_approved' else po.status.upper()

            self.stdout.write(
                f"  Batch {batch.batch_id}: {items_count} products, ${value:.2f} ({status_display})"
            )

        self.stdout.write(
            self.style.SUCCESS(f"\nTOTAL: {total_products} products replenished, ${total_value:.2f} value")
        )
