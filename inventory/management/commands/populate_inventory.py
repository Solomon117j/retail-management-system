import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from inventory.models import Product, InventoryRecord, StockMovement
from store_management.models import Store
from human_resources.models import Employee


class Command(BaseCommand):
    help = 'Populate inventory records and stock movements for products across stores'

    def handle(self, *args, **options):
        # Get all products and stores
        products = list(Product.objects.all())
        stores = list(Store.objects.all())
        employees = list(Employee.objects.all())

        if not products or not stores:
            self.stdout.write(self.style.ERROR('No products or stores found. Please run populate_data.py first.'))
            return

        self.stdout.write(f'Found {len(products)} products and {len(stores)} stores')

        # Create inventory records for products across stores
        inventory_records = []
        stock_movements = []

        for product in products:
            # Randomly assign product to 1-3 stores
            num_stores = random.randint(1, min(3, len(stores)))
            selected_stores = random.sample(stores, num_stores)

            for store in selected_stores:
                # Create inventory record with random stock
                quantity = random.randint(0, 100)  # Some products will have 0 stock
                inventory_record, created = InventoryRecord.objects.get_or_create(
                    product=product,
                    store=store,
                    defaults={
                        'quantity': quantity,
                        'location': f'Shelf {random.randint(1, 10)}',
                        'cost_price': product.unit_price * Decimal('0.6'),  # 60% of selling price
                        'last_updated_by': random.choice(employees) if employees else None
                    }
                )

                if created:
                    inventory_records.append(inventory_record)

                    # Create initial stock movement if quantity > 0
                    if quantity > 0:
                        movement = StockMovement.objects.create(
                            product=product,
                            store=store,
                            quantity=quantity,
                            movement_type='IN',
                            reason='PURCHASE',
                            reference=f'Initial Stock',
                            created_by=random.choice(employees) if employees else None
                        )
                        stock_movements.append(movement)

        self.stdout.write(f'Created {len(inventory_records)} inventory records')
        self.stdout.write(f'Created {len(stock_movements)} initial stock movements')

        # Show some examples
        self.stdout.write('\nSample inventory records:')
        for record in InventoryRecord.objects.select_related('product', 'store')[:10]:
            self.stdout.write(f'{record.product.name} at {record.store.name}: {record.quantity} units')
