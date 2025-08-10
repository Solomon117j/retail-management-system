#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from inventory.models import Product, Category, Brand
from inventory.forms import ProductForm

def test_product_form():
    """Test the product form with valid data"""
    
    # Get a category and brand
    category = Category.objects.first()
    brand = Brand.objects.first()
    
    if not category:
        print("No categories found. Please run populate_inventory.py first.")
        return
    
    if not brand:
        print("No brands found. Please run populate_inventory.py first.")
        return
    
    # Test form data
    form_data = {
        'name': 'Test Product',
        'description': 'This is a test product',
        'category': category.id,
        'brand': brand.id,
        'unit_price': '19.99',
        'cost_price': '10.00',
        'weight': '1.5',
        'dimensions': '10x5x3',
        'is_perishable': False,
        'barcode': '1234567890123'
    }
    
    print("Testing product form with data:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    form = ProductForm(data=form_data)
    
    if form.is_valid():
        print("\n✅ Form is valid!")
        product = form.save()
        print(f"✅ Product created successfully: {product.name} (ID: {product.id})")
        
        # Clean up - delete the test product
        product.delete()
        print("✅ Test product deleted")
        
    else:
        print("\n❌ Form is invalid!")
        print("Errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

def test_required_fields():
    """Test form with missing required fields"""
    print("\n" + "="*50)
    print("Testing form with missing required fields...")
    
    form_data = {
        'description': 'This product is missing required fields',
        'is_perishable': False,
    }
    
    form = ProductForm(data=form_data)
    
    if form.is_valid():
        print("❌ Form should not be valid with missing required fields!")
    else:
        print("✅ Form correctly rejected missing required fields")
        print("Required field errors:")
        for field, errors in form.errors.items():
            if field in ['name', 'category', 'unit_price']:
                print(f"  {field}: {errors}")

if __name__ == '__main__':
    print("Testing Product Form...")
    print("="*50)
    
    # Check if we have categories and brands
    cat_count = Category.objects.count()
    brand_count = Brand.objects.count()
    
    print(f"Categories in database: {cat_count}")
    print(f"Brands in database: {brand_count}")
    
    if cat_count == 0 or brand_count == 0:
        print("\n❌ Missing categories or brands. Running populate script...")
        from populate_inventory import populate_categories, populate_brands
        populate_categories()
        populate_brands()
    
    print("\n" + "="*50)
    test_product_form()
    test_required_fields()
    print("\n" + "="*50)
    print("Test completed!")