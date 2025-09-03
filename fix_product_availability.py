#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from inventory.models import Product

def fix_product_availability():
    """Set available_online=True for products that have stock in inventory"""
    # Get products that have stock but are not available online
    products_to_update = Product.objects.filter(
        inventory_records__quantity__gt=0,
        available_online=False
    ).distinct()

    updated_count = 0
    for product in products_to_update:
        product.available_online = True
        product.save(update_fields=['available_online'])
        updated_count += 1
        print(f"Updated product: {product.name} (ID: {product.id})")

    print(f"Total products updated: {updated_count}")

    # Also check if there are products with available_online=True but no stock
    products_to_hide = Product.objects.filter(
        available_online=True
    ).exclude(
        inventory_records__quantity__gt=0
    ).distinct()

    hidden_count = 0
    for product in products_to_hide:
        product.available_online = False
        product.save(update_fields=['available_online'])
        hidden_count += 1
        print(f"Hidden product (no stock): {product.name} (ID: {product.id})")

    print(f"Total products hidden: {hidden_count}")

if __name__ == '__main__':
    print("Fixing product availability for customer portal...")
    fix_product_availability()
    print("Done!")
