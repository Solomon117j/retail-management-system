#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from inventory.models import Product, StoreInventory
from store_management.models import Store

def add_inventory():
    """Add inventory to products that don't have any"""
    # Get all products available online
    products = Product.objects.filter(available_online=True)
    stores = Store.objects.all()

    if not stores:
        print("No stores found.")
        return

    for product in products:
        has_inventory = product.inventory_records.exists()
        if not has_inventory:
            print(f"Adding inventory for: {product.name}")
            for store in stores:
                try:
                    inventory, created = StoreInventory.objects.get_or_create(
                        product=product,
                        store=store,
                        defaults={'quantity': 50}
                    )
                    if created:
                        print(f"  Created inventory at {store.store_name}: 50 units")
                    else:
                        print(f"  Inventory already exists at {store.store_name}")
                except Exception as e:
                    print(f"  Error creating inventory at {store.store_name}: {e}")
        else:
            print(f"Product {product.name} already has inventory")

    print(f"\nSummary:")
    print(f"Products available online: {Product.objects.filter(available_online=True).count()}")
    print(f"Products with inventory > 0: {Product.objects.filter(inventory_records__quantity__gt=0).distinct().count()}")
    print(f"Products ready for e-commerce: {Product.objects.filter(available_online=True, inventory_records__quantity__gt=0).distinct().count()}")

if __name__ == '__main__':
    print("Adding inventory to products...")
    add_inventory()
    print("Done!")
