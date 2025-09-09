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

def make_products_online():
    """Make existing inventory products available online"""
    # Find products that have inventory but are not available online
    products_to_update = Product.objects.filter(
        inventory_records__quantity__gt=0,
        available_online=False
    ).distinct()

    updated_count = 0
    for product in products_to_update:
        product.available_online = True
        product.save()
        print(f"Made product available online: {product.name}")
        updated_count += 1

    print(f"\nSummary:")
    print(f"Products made available online: {updated_count}")
    print(f"Total products available online: {Product.objects.filter(available_online=True).count()}")
    print(f"Total products with inventory: {Product.objects.filter(inventory_records__quantity__gt=0).distinct().count()}")
    print(f"Products ready for e-commerce: {Product.objects.filter(available_online=True, inventory_records__quantity__gt=0).distinct().count()}")

if __name__ == '__main__':
    print("Making inventory products available online...")
    make_products_online()
    print("Done!")
