import random
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from inventory.models import Product, Brand, Category
from procurement.models import Supplier, SupplierProduct


class Command(BaseCommand):
    help = 'Generate sample medical supplies and equipment data with enterprise-ready information'

    def handle(self, *args, **options):
        # Predefined categories for medical products
        category_data = [
            {'name': 'Medical Supplies', 'description': 'Essential consumable items for medical care'},
            {'name': 'Medical Equipment', 'description': 'Durable medical devices and equipment'},
            {'name': 'Pharmaceuticals', 'description': 'Medicines and pharmaceutical products'},
            {'name': 'Diagnostic Equipment', 'description': 'Tools and devices for medical diagnosis'},
            {'name': 'Surgical Instruments', 'description': 'Instruments used in surgical procedures'},
            {'name': 'Protective Gear', 'description': 'Personal protective equipment for healthcare workers'},
            {'name': 'Laboratory Supplies', 'description': 'Supplies for medical laboratories and testing'},
        ]

        # Predefined brands
        brand_data = [
            {'name': 'Johnson & Johnson', 'description': 'Global healthcare company'},
            {'name': 'Pfizer', 'description': 'Leading pharmaceutical company'},
            {'name': 'Medtronic', 'description': 'Medical device company'},
            {'name': 'Siemens Healthineers', 'description': 'Medical technology company'},
            {'name': 'GE Healthcare', 'description': 'Healthcare technology solutions'},
            {'name': 'Philips Healthcare', 'description': 'Health technology company'},
            {'name': 'Becton Dickinson', 'description': 'Medical technology company'},
            {'name': 'Abbott Laboratories', 'description': 'Healthcare company'},
            {'name': 'Thermo Fisher Scientific', 'description': 'Scientific research company'},
            {'name': 'Roche Diagnostics', 'description': 'Diagnostics company'},
        ]



        # Sample products with enterprise-ready information
        product_data = [
            # Medical Supplies
            {'name': 'Latex Examination Gloves', 'description': 'Powder-free latex gloves for medical examination', 'category': 'Medical Supplies', 'brand': 'Becton Dickinson', 'unit_price': Decimal('15.99'), 'reorder_level': 500},
            {'name': 'Surgical Face Masks', 'description': 'Disposable surgical masks with ear loops', 'category': 'Medical Supplies', 'brand': 'Johnson & Johnson', 'unit_price': Decimal('8.50'), 'reorder_level': 1000},
            {'name': 'Bandages - Adhesive Strips', 'description': 'Assorted adhesive bandage strips for wound care', 'category': 'Medical Supplies', 'brand': 'Johnson & Johnson', 'unit_price': Decimal('12.99'), 'reorder_level': 300},
            {'name': 'Syringes - 10ml', 'description': 'Disposable syringes with needles for injections', 'category': 'Medical Supplies', 'brand': 'Becton Dickinson', 'unit_price': Decimal('22.50'), 'reorder_level': 200},
            {'name': 'Alcohol Swabs', 'description': 'Sterile alcohol prep pads for disinfection', 'category': 'Medical Supplies', 'brand': 'Johnson & Johnson', 'unit_price': Decimal('5.99'), 'reorder_level': 800},

            # Medical Equipment
            {'name': 'Digital Blood Pressure Monitor', 'description': 'Automatic blood pressure monitor with LCD display', 'category': 'Medical Equipment', 'brand': 'Philips Healthcare', 'unit_price': Decimal('89.99'), 'reorder_level': 50},
            {'name': 'Stethoscope - Professional', 'description': 'Dual-head stethoscope for medical professionals', 'category': 'Medical Equipment', 'brand': 'Philips Healthcare', 'unit_price': Decimal('45.00'), 'reorder_level': 30},
            {'name': 'Thermometer - Digital', 'description': 'Non-contact infrared thermometer for temperature measurement', 'category': 'Medical Equipment', 'brand': 'GE Healthcare', 'unit_price': Decimal('35.99'), 'reorder_level': 75},
            {'name': 'Pulse Oximeter', 'description': 'Portable device for measuring blood oxygen saturation', 'category': 'Medical Equipment', 'brand': 'Philips Healthcare', 'unit_price': Decimal('65.50'), 'reorder_level': 40},
            {'name': 'Defibrillator - Portable', 'description': 'Automated external defibrillator for emergency cardiac care', 'category': 'Medical Equipment', 'brand': 'Philips Healthcare', 'unit_price': Decimal('2999.99'), 'reorder_level': 5},

            # Pharmaceuticals
            {'name': 'Paracetamol Tablets 500mg', 'description': 'Pain relief and fever reduction medication', 'category': 'Pharmaceuticals', 'brand': 'Pfizer', 'unit_price': Decimal('4.99'), 'reorder_level': 1000},
            {'name': 'Ibuprofen 200mg Tablets', 'description': 'Anti-inflammatory pain relief medication', 'category': 'Pharmaceuticals', 'brand': 'Pfizer', 'unit_price': Decimal('6.50'), 'reorder_level': 800},
            {'name': 'Amoxicillin 500mg Capsules', 'description': 'Antibiotic medication for bacterial infections', 'category': 'Pharmaceuticals', 'brand': 'Pfizer', 'unit_price': Decimal('12.99'), 'reorder_level': 500},
            {'name': 'Vitamin D3 Supplements', 'description': 'Dietary supplements for bone health', 'category': 'Pharmaceuticals', 'brand': 'Abbott Laboratories', 'unit_price': Decimal('18.99'), 'reorder_level': 300},
            {'name': 'Insulin Injection Pens', 'description': 'Disposable insulin pens for diabetes management', 'category': 'Pharmaceuticals', 'brand': 'Roche Diagnostics', 'unit_price': Decimal('45.00'), 'reorder_level': 100},

            # Diagnostic Equipment
            {'name': 'Ultrasound Machine - Portable', 'description': 'Handheld ultrasound device for point-of-care diagnostics', 'category': 'Diagnostic Equipment', 'brand': 'GE Healthcare', 'unit_price': Decimal('2500.00'), 'reorder_level': 10},
            {'name': 'ECG Machine - 12-Lead', 'description': 'Electrocardiogram machine for heart monitoring', 'category': 'Diagnostic Equipment', 'brand': 'Philips Healthcare', 'unit_price': Decimal('1800.99'), 'reorder_level': 8},
            {'name': 'X-Ray Machine - Digital', 'description': 'Digital radiography system for medical imaging', 'category': 'Diagnostic Equipment', 'brand': 'Siemens Healthineers', 'unit_price': Decimal('15000.00'), 'reorder_level': 2},
            {'name': 'Blood Glucose Monitor', 'description': 'Device for monitoring blood glucose levels', 'category': 'Diagnostic Equipment', 'brand': 'Roche Diagnostics', 'unit_price': Decimal('29.99'), 'reorder_level': 60},
            {'name': 'Spirometer', 'description': 'Device for measuring lung function', 'category': 'Diagnostic Equipment', 'brand': 'Philips Healthcare', 'unit_price': Decimal('199.99'), 'reorder_level': 25},

            # Surgical Instruments
            {'name': 'Surgical Scalpel Blades', 'description': 'Sterile surgical blades for precision cutting', 'category': 'Surgical Instruments', 'brand': 'Johnson & Johnson', 'unit_price': Decimal('25.99'), 'reorder_level': 200},
            {'name': 'Forceps - Surgical', 'description': 'Precision surgical forceps for tissue handling', 'category': 'Surgical Instruments', 'brand': 'Becton Dickinson', 'unit_price': Decimal('35.50'), 'reorder_level': 100},
            {'name': 'Surgical Scissors', 'description': 'High-quality stainless steel surgical scissors', 'category': 'Surgical Instruments', 'brand': 'Johnson & Johnson', 'unit_price': Decimal('28.99'), 'reorder_level': 150},
            {'name': 'Hemostatic Clamps', 'description': 'Surgical clamps for controlling blood flow', 'category': 'Surgical Instruments', 'brand': 'Medtronic', 'unit_price': Decimal('42.00'), 'reorder_level': 80},
            {'name': 'Surgical Needle Holders', 'description': 'Precision instruments for suturing', 'category': 'Surgical Instruments', 'brand': 'Becton Dickinson', 'unit_price': Decimal('55.99'), 'reorder_level': 60},

            # Protective Gear
            {'name': 'N95 Respirator Masks', 'description': 'High-filtration respiratory protection masks', 'category': 'Protective Gear', 'brand': 'Johnson & Johnson', 'unit_price': Decimal('12.99'), 'reorder_level': 500},
            {'name': 'Surgical Gowns - Disposable', 'description': 'Sterile disposable gowns for surgical procedures', 'category': 'Protective Gear', 'brand': 'Medtronic', 'unit_price': Decimal('18.50'), 'reorder_level': 300},
            {'name': 'Face Shields', 'description': 'Transparent face protection shields', 'category': 'Protective Gear', 'brand': 'Philips Healthcare', 'unit_price': Decimal('8.99'), 'reorder_level': 400},
            {'name': 'Protective Eyewear', 'description': 'Safety goggles for eye protection', 'category': 'Protective Gear', 'brand': 'Johnson & Johnson', 'unit_price': Decimal('15.99'), 'reorder_level': 250},
            {'name': 'Disposable Coveralls', 'description': 'Full-body protective suits for hazardous environments', 'category': 'Protective Gear', 'brand': 'Medtronic', 'unit_price': Decimal('25.99'), 'reorder_level': 200},

            # Laboratory Supplies
            {'name': 'Microscope Slides', 'description': 'Glass slides for microscopic examination', 'category': 'Laboratory Supplies', 'brand': 'Thermo Fisher Scientific', 'unit_price': Decimal('9.99'), 'reorder_level': 1000},
            {'name': 'Test Tubes - 15ml', 'description': 'Disposable test tubes for laboratory use', 'category': 'Laboratory Supplies', 'brand': 'Thermo Fisher Scientific', 'unit_price': Decimal('7.50'), 'reorder_level': 500},
            {'name': 'Pipette Tips - 1000µl', 'description': 'Sterile pipette tips for accurate liquid handling', 'category': 'Laboratory Supplies', 'brand': 'Thermo Fisher Scientific', 'unit_price': Decimal('14.99'), 'reorder_level': 300},
            {'name': 'Centrifuge Tubes', 'description': 'Conical tubes for centrifugation procedures', 'category': 'Laboratory Supplies', 'brand': 'Thermo Fisher Scientific', 'unit_price': Decimal('11.99'), 'reorder_level': 400},
            {'name': 'Petri Dishes', 'description': 'Sterile dishes for microbial culture', 'category': 'Laboratory Supplies', 'brand': 'Thermo Fisher Scientific', 'unit_price': Decimal('6.99'), 'reorder_level': 600},
        ]

        # Create categories if they don't exist
        categories_created = 0
        category_objects = {}
        for cat_data in category_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            category_objects[cat_data['name']] = category
            if created:
                categories_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create brands if they don't exist
        brands_created = 0
        brand_objects = {}
        for brand_data_item in brand_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data_item['name'],
                defaults={'description': brand_data_item['description']}
            )
            brand_objects[brand_data_item['name']] = brand
            if created:
                brands_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created brand: {brand.name}'))

        # Get all existing suppliers from the database (assuming they were created by generate_sample_suppliers command)
        suppliers = list(Supplier.objects.all())
        if not suppliers:
            self.stdout.write(self.style.ERROR('No suppliers found in the database. Please run the generate_sample_suppliers command first.'))
            return

        # Create products
        products_created = 0
        for prod_data in product_data:
            # Generate unique SKU
            sku = f"{prod_data['brand'][:3].upper()}-{prod_data['category'][:3].upper()}-{random.randint(1000, 9999)}"
            while Product.objects.filter(sku=sku).exists():
                sku = f"{prod_data['brand'][:3].upper()}-{prod_data['category'][:3].upper()}-{random.randint(1000, 9999)}"

            # Generate unique barcode
            barcode = str(uuid.uuid4().int)[:13]
            while Product.objects.filter(barcode=barcode).exists():
                barcode = str(uuid.uuid4().int)[:13]

            # Random dimensions and weight based on category
            if prod_data['category'] in ['Medical Supplies', 'Protective Gear', 'Laboratory Supplies']:
                weight = round(random.uniform(0.01, 0.5), 2)
                length = round(random.uniform(5, 20), 2)
                width = round(random.uniform(5, 15), 2)
                height = round(random.uniform(1, 5), 2)
            elif prod_data['category'] in ['Medical Equipment', 'Diagnostic Equipment']:
                weight = round(random.uniform(0.5, 5.0), 2)
                length = round(random.uniform(10, 50), 2)
                width = round(random.uniform(10, 40), 2)
                height = round(random.uniform(5, 30), 2)
            else:
                weight = round(random.uniform(0.01, 2.0), 2)
                length = round(random.uniform(5, 30), 2)
                width = round(random.uniform(5, 25), 2)
                height = round(random.uniform(1, 15), 2)

            # Random default supplier
            default_supplier = random.choice(suppliers) if suppliers and random.choice([True, False]) else None

            # Create the product
            product = Product.objects.create(
                name=prod_data['name'],
                description=prod_data['description'],
                category=category_objects[prod_data['category']],
                brand=brand_objects[prod_data['brand']],
                sku=sku,
                unit_price=prod_data['unit_price'],
                reorder_level=prod_data['reorder_level'],
                is_active=True,
                barcode=barcode,
                weight=weight,
                length=length,
                width=width,
                height=height,
                default_supplier=default_supplier,
            )

            products_created += 1
            self.stdout.write(self.style.SUCCESS(f'Created product: {product.name} (SKU: {product.sku})'))

        # Create supplier-product relationships
        supplier_products_created = 0
        for product in Product.objects.all():
            # Select 1-3 random suppliers for each product
            num_suppliers = random.randint(1, 3)
            selected_suppliers = random.sample(suppliers, min(num_suppliers, len(suppliers)))

            for supplier in selected_suppliers:
                # Calculate supply price (10-30% discount from unit price)
                discount_factor = random.uniform(0.7, 0.9)  # 10-30% discount
                supply_price = round(float(product.unit_price) * discount_factor, 2)

                # Random lead time (1-14 days)
                lead_time = random.randint(1, 14)

                # Random minimum order quantity (1-50)
                min_order_qty = random.randint(1, 50)

                # Create supplier-product link
                supplier_product, created = SupplierProduct.objects.get_or_create(
                    supplier=supplier,
                    product=product,
                    defaults={
                        'supply_price': Decimal(str(supply_price)),
                        'lead_time': lead_time,
                        'minimum_order_quantity': min_order_qty,
                    }
                )
                if created:
                    supplier_products_created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Created supplier-product link: {product.name} from {supplier.name} (${supply_price})'
                    ))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {categories_created} categories, {brands_created} brands, {products_created} products, and {supplier_products_created} supplier-product relationships.'
        ))
