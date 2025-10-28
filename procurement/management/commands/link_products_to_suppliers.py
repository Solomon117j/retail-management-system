from django.core.management.base import BaseCommand
from inventory.models import Product
from procurement.models import Supplier, SupplierProduct

class Command(BaseCommand):
    help = 'Link existing products to their default suppliers by creating SupplierProduct records'

    def handle(self, *args, **options):
        products = Product.objects.filter(default_supplier__isnull=False)

        for product in products:
            # Check if SupplierProduct already exists
            if not SupplierProduct.objects.filter(supplier=product.default_supplier, product=product).exists():
                # Create SupplierProduct with default values
                supplier_product = SupplierProduct.objects.create(
                    supplier=product.default_supplier,
                    product=product,
                    supply_price=product.unit_price,  # Use product unit price as supply price
                    lead_time=7,  # Default lead time of 7 days
                    minimum_order_quantity=1,
                    preferred_supplier=True  # Mark as preferred since it's the default
                )
                self.stdout.write(self.style.SUCCESS(f'Linked product: {product.name} to supplier: {product.default_supplier.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product {product.name} already linked to supplier {product.default_supplier.name}'))

        self.stdout.write(self.style.SUCCESS('Product-supplier linking completed.'))
