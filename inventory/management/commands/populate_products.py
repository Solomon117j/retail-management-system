from django.core.management.base import BaseCommand
from inventory.models import Product, Category, Brand
from procurement.models import Supplier

class Command(BaseCommand):
    help = 'Populate products with provided data (prices in ZAR)'

    def handle(self, *args, **options):
        products_data = [
            {
                'name': 'Sterile Urine Collection Cup 100ml',
                'sku': 'LAS-UR-STER100',
                'barcode': '6009991234611',
                'supplier_name': 'Lasec SA',
                'category_name': 'Specimen Container',
                'brand_name': 'LabPure',
                'unit_price': 4.50,  # ZAR
                'reorder_level': 200,
                'weight_g': 15,
                'width': 6,
                'length': 6,
                'height': 9,
                'description': 'Clear plastic, sterile, leak-proof cap, 100ml capacity, graduated.',
            },
            {
                'name': 'Non-Sterile Urine Jar 500ml',
                'sku': 'AMA-UR-NS500',
                'barcode': '6009991234628',
                'supplier_name': 'Amayeza Abantu',
                'category_name': 'Specimen Container',
                'brand_name': 'MediCollect',
                'unit_price': 8.20,  # ZAR
                'reorder_level': 100,
                'weight_g': 45,
                'width': 9,
                'length': 9,
                'height': 14,
                'description': 'Wide-mouth, non-sterile jar with secure screw cap, 500ml capacity.',
            },
            {
                'name': '24hr Urine Collection Jug 3L',
                'sku': 'LRC-UR-24H3L',
                'barcode': '6009991234635',
                'supplier_name': 'Lohmann & Rauscher',
                'category_name': 'Specimen Container',
                'brand_name': 'UroCare',
                'unit_price': 22.00,  # ZAR
                'reorder_level': 50,
                'weight_g': 180,
                'width': 16,
                'length': 16,
                'height': 22,
                'description': 'Large 3-litre capacity jug for 24-hour urine collection, with handle.',
            },
            {
                'name': 'Urine Specimen Cup with Lid 60ml',
                'sku': 'DCM-UR-CUP60',
                'barcode': '6009991234642',
                'supplier_name': 'Dis-Chem Direct',
                'category_name': 'Specimen Container',
                'brand_name': 'SafePath',
                'unit_price': 3.80,  # ZAR
                'reorder_level': 150,
                'weight_g': 10,
                'width': 5,
                'length': 5,
                'height': 7,
                'description': 'Small, disposable cup with snap-on lid, 60ml, non-sterile.',
            },
        ]

        for data in products_data:
            # Get or create category
            category, _ = Category.objects.get_or_create(name=data['category_name'])

            # Get or create brand
            brand, _ = Brand.objects.get_or_create(name=data['brand_name'])

            # Get supplier
            try:
                supplier = Supplier.objects.get(name=data['supplier_name'])
            except Supplier.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Supplier '{data['supplier_name']}' not found. Skipping product '{data['name']}'."))
                continue

            # Convert weight from g to kg
            weight_kg = data['weight_g'] / 1000 if data['weight_g'] else None

            # Create or update product
            product, created = Product.objects.get_or_create(
                sku=data['sku'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'category': category,
                    'brand': brand,
                    'unit_price': data['unit_price'],
                    'reorder_level': data['reorder_level'],
                    'barcode': data['barcode'],
                    'weight': weight_kg,
                    'length': data['length'],
                    'width': data['width'],
                    'height': data['height'],
                    'default_supplier': supplier,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                # Update existing product
                product.name = data['name']
                product.description = data['description']
                product.category = category
                product.brand = brand
                product.unit_price = data['unit_price']
                product.reorder_level = data['reorder_level']
                product.barcode = data['barcode']
                product.weight = weight_kg
                product.length = data['length']
                product.width = data['width']
                product.height = data['height']
                product.default_supplier = supplier
                product.save()
                self.stdout.write(self.style.WARNING(f'Updated product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Product population completed (all prices in ZAR).'))
