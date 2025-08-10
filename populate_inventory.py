#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from inventory.models import Category, Brand

def populate_categories():
    """Create some default categories if they don't exist"""
    categories = [
        {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
        {'name': 'Clothing', 'description': 'Apparel and fashion items'},
        {'name': 'Food & Beverages', 'description': 'Food items and drinks'},
        {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
        {'name': 'Health & Beauty', 'description': 'Health and beauty products'},
        {'name': 'Sports & Outdoors', 'description': 'Sports equipment and outdoor gear'},
        {'name': 'Books & Media', 'description': 'Books, movies, and media'},
        {'name': 'Toys & Games', 'description': 'Toys and gaming products'},
    ]
    
    created_count = 0
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            created_count += 1
            print(f"Created category: {category.name}")
    
    print(f"Categories: {created_count} created, {Category.objects.count()} total")

def populate_brands():
    """Create some default brands if they don't exist"""
    brands = [
        {'name': 'Generic', 'description': 'Generic brand for unbranded products'},
        {'name': 'Samsung', 'description': 'Samsung Electronics'},
        {'name': 'Apple', 'description': 'Apple Inc.'},
        {'name': 'Nike', 'description': 'Nike sportswear'},
        {'name': 'Adidas', 'description': 'Adidas sportswear'},
        {'name': 'Sony', 'description': 'Sony Corporation'},
        {'name': 'LG', 'description': 'LG Electronics'},
        {'name': 'Coca-Cola', 'description': 'The Coca-Cola Company'},
    ]
    
    created_count = 0
    for brand_data in brands:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults={'description': brand_data['description']}
        )
        if created:
            created_count += 1
            print(f"Created brand: {brand.name}")
    
    print(f"Brands: {created_count} created, {Brand.objects.count()} total")

if __name__ == '__main__':
    print("Populating inventory data...")
    populate_categories()
    populate_brands()
    print("Done!")