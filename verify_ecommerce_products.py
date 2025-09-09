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
from django.db import models

def verify_products():
    """Verify products available online"""
    print("Products available online:")
    online_products = Product.objects.filter(available_online=True).select_related('category', 'brand')
    for product in online_products:
        total_stock = product.inventory_records.aggregate(total=models.Sum('quantity'))['total'] or 0
        print(f"- {product.name} (Category: {product.category.name if product.category else 'N/A'}, Stock: {total_stock})")

    print(f"\nTotal products available online: {online_products.count()}")

    # Check products with inventory but not online
    offline_with_stock = Product.objects.filter(
        inventory_records__quantity__gt=0,
        available_online=False
    ).distinct()
    if offline_with_stock.exists():
        print(f"\nWarning: {offline_with_stock.count()} products have inventory but are not available online:")
        for product in offline_with_stock:
            print(f"- {product.name}")
    else:
        print("\nAll products with inventory are available online.")

if __name__ == '__main__':
    print("Verifying e-commerce products...")
    verify_products()
    print("Verification complete!")
