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

def check_products():
    """Check all products and their image status"""
    products = Product.objects.all()

    print(f"Total products: {products.count()}")
    print("\nProduct Image Status:")
    print("-" * 50)

    products_with_images = 0
    products_without_images = 0

    for product in products:
        if product.image:
            print(f"✓ {product.name}: {product.image}")
            products_with_images += 1
        else:
            print(f"✗ {product.name}: No image")
            products_without_images += 1

    print("\nSummary:")
    print(f"Products with images: {products_with_images}")
    print(f"Products without images: {products_without_images}")

    # Check available online products
    online_products = Product.objects.filter(available_online=True)
    print(f"\nOnline products: {online_products.count()}")

    online_with_images = 0
    online_without_images = 0

    for product in online_products:
        if product.image:
            online_with_images += 1
        else:
            online_without_images += 1

    print(f"Online products with images: {online_with_images}")
    print(f"Online products without images: {online_without_images}")

if __name__ == '__main__':
    check_products()
