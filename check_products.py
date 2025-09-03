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
from django.db.models import Sum

def check_products():
    print("=== Products with Stock ===")
    products_with_stock = Product.objects.filter(
        inventory_records__quantity__gt=0
    ).select_related('category', 'brand').distinct()

    for product in products_with_stock:
        total_stock = product.inventory_records.aggregate(total=Sum('quantity'))['total'] or 0
        print(f"{product.name} (ID: {product.id}) - Stock: {total_stock}, Available Online: {product.available_online}")

    print(f"\nTotal products with stock: {products_with_stock.count()}")

    print("\n=== All Products ===")
    all_products = Product.objects.all().select_related('category', 'brand')
    for product in all_products:
        has_stock = product.inventory_records.filter(quantity__gt=0).exists()
        total_stock = product.inventory_records.aggregate(total=Sum('quantity'))['total'] or 0
        print(f"{product.name} (ID: {product.id}) - Has Stock: {has_stock}, Stock: {total_stock}, Available Online: {product.available_online}")

    print(f"\nTotal products: {all_products.count()}")

if __name__ == '__main__':
    check_products()
