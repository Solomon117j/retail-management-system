#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from inventory.models import Product, Category, Brand, StoreInventory
from store_management.models import Store

def populate_products():
    """Create some test products for e-commerce"""
    # Get categories and brands
    categories = list(Category.objects.all()[:4])  # Get first 4 categories
    brands = list(Brand.objects.all()[:4])  # Get first 4 brands

    if not categories:
        print("No categories found. Run populate_inventory.py first.")
        return
    if not brands:
        print("No brands found. Run populate_inventory.py first.")
        return

    # Get stores
    stores = list(Store.objects.all())
    if not stores:
        print("No stores found. Create stores first.")
        return

    products_data = [
        {
            'name': 'Wireless Headphones',
            'description': 'High-quality wireless headphones with noise cancellation',
            'category': categories[0] if len(categories) > 0 else categories[0],
            'brand': brands[0] if len(brands) > 0 else brands[0],
            'unit_price': 199.99,
            'cost_price': 120.00,
            'available_online': True,
        },
        {
            'name': 'Smartphone Case',
            'description': 'Protective case for smartphones',
            'category': categories[0] if len(categories) > 0 else categories[0],
            'brand': brands[1] if len(brands) > 1 else brands[0],
            'unit_price': 29.99,
            'cost_price': 15.00,
            'available_online': True,
        },
        {
            'name': 'Running Shoes',
            'description': 'Comfortable running shoes for athletes',
            'category': categories[1] if len(categories) > 1 else categories[0],
            'brand': brands[2] if len(brands) > 2 else brands[0],
            'unit_price': 149.99,
            'cost_price': 80.00,
            'available_online': True,
        },
        {
            'name': 'Coffee Maker',
            'description': 'Automatic coffee maker for home use',
            'category': categories[2] if len(categories) > 2 else categories[0],
            'brand': brands[3] if len(brands) > 3 else brands[0],
            'unit_price': 89.99,
            'cost_price': 50.00,
            'available_online': True,
        },
        {
            'name': 'Yoga Mat',
            'description': 'Non-slip yoga mat for exercise',
            'category': categories[3] if len(categories) > 3 else categories[0],
            'brand': brands[0] if len(brands) > 0 else brands[0],
            'unit_price': 39.99,
            'cost_price': 20.00,
            'available_online': True,
        },
    ]

    created_products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            print(f"Created product: {product.name}")
            created_products.append(product)
        else:
            # Update if exists but not available_online
            if not product.available_online:
                product.available_online = True
                product.save()
                print(f"Updated product: {product.name} (set available_online=True)")

    # Create inventory for each product in each store
    for product in created_products:
        for store in stores:
            inventory, created = StoreInventory.objects.get_or_create(
                product=product,
                store=store,
                defaults={'quantity': 50}  # Default quantity
            )
            if created:
                print(f"Created inventory: {product.name} at {store.store_name} (qty: 50)")
            else:
                # Ensure quantity > 0
                if inventory.quantity <= 0:
                    inventory.quantity = 50
                    inventory.save()
                    print(f"Updated inventory: {product.name} at {store.store_name} (qty: 50)")

    print(f"\nSummary:")
    print(f"Products available online: {Product.objects.filter(available_online=True).count()}")
    print(f"Products with inventory > 0: {Product.objects.filter(inventory_records__quantity__gt=0).distinct().count()}")
    print(f"Products ready for e-commerce: {Product.objects.filter(available_online=True, inventory_records__quantity__gt=0).distinct().count()}")

if __name__ == '__main__':
    print("Populating e-commerce test products...")
    populate_products()
    print("Done!")
