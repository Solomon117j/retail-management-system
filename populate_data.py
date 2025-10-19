#!/usr/bin/env python
"""
Script to populate the retail management system with sample data.
This script creates suppliers, stores, departments, employees, and products in the correct order.
"""

import os
import django
import random
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from procurement.models import Supplier
from store_management.models import Store, Department
from human_resources.models import Employee
from inventory.models import Product, Brand, Category

def create_suppliers():
    """Create sample suppliers"""
    suppliers = []
    supplier_data = [
        {
            'name': 'Global Electronics Ltd',
            'contact_person': 'Thembinkosi Dlamini',
            'email': 'thembinkosid@globalelectronics.com',
            'phone': '+268 2406 1000',
            'address': '123 Industrial Road, Matsapha',
            'payment_terms': 'Net 30',
            'industry': 'Electronics',
        },
        {
            'name': 'Fashion Forward Inc',
            'contact_person': 'Thabile Dlamini',
            'email': 'thabiled@fashionforward.com',
            'phone': '+268 2506 2000',
            'address': '456 Fashion Street, Manzini',
            'payment_terms': 'Net 15',
            'industry': 'Fashion',
        },
        {
            'name': 'Home & Garden Supplies',
            'contact_person': 'Zandile Mabuza',
            'email': 'zandilem@homegarden.com',
            'phone': '+268 2406 3000',
            'address': '789 Garden Avenue, Mbabane',
            'payment_terms': 'Net 45',
            'industry': 'Home & Garden',
        },
        {
            'name': 'Sports Equipment Co',
            'contact_person': 'Mbuso Dlamini',
            'email': 'mbusom@sportsequip.com',
            'phone': '+268 2406 4000',
            'address': '321 Sports Complex, Siteki',
            'payment_terms': 'Net 30',
            'industry': 'Sports',
        },
        {
            'name': 'Book World Publishers',
            'contact_person': 'Frank Mndzebele',
            'email': 'frankm@bookworld.com',
            'phone': '+268 2406 5000',
            'address': '654 Library Road, Nhlangano',
            'payment_terms': 'Net 60',
            'industry': 'Publishing',
        },
    ]

    for data in supplier_data:
        supplier = Supplier.objects.create(**data)
        suppliers.append(supplier)
        print(f"Created supplier: {supplier.name}")

    return suppliers

def create_stores():
    """Create sample stores"""
    stores = []
    store_data = [
        {
            'name': 'Mbabane Central Store',
            'address': '123 Main Street',
            'city': 'Mbabane',
            'region': 'Hhohho',
            'postal_code': 'H100',
            'phone': '+268 2406 0001',
            'email': 'mbabane@retail.com',
            'store_type': 'flagship',
            'opening_date': '2020-01-15',
        },
        {
            'name': 'Manzini Mall Store',
            'address': '456 Shopping Center',
            'city': 'Manzini',
            'region': 'Manzini',
            'postal_code': 'M200',
            'phone': '+268 2406 0002',
            'email': 'manzini@retail.com',
            'store_type': 'retail',
            'opening_date': '2020-03-20',
        },
        {
            'name': 'Matsapha Outlet',
            'address': '789 Industrial Area',
            'city': 'Matsapha',
            'region': 'Manzini',
            'postal_code': 'M300',
            'phone': '+268 2406 0003',
            'email': 'matsapha@retail.com',
            'store_type': 'outlet',
            'opening_date': '2021-06-10',
        },
        {
            'name': 'Siteki Branch',
            'address': '321 Rural Road',
            'city': 'Siteki',
            'region': 'Lubombo',
            'postal_code': 'L400',
            'phone': '+268 2406 0004',
            'email': 'siteki@retail.com',
            'store_type': 'retail',
            'opening_date': '2021-09-05',
        },
        {
            'name': 'Nhlangano Store',
            'address': '654 Border Road',
            'city': 'Nhlangano',
            'region': 'Shiselweni',
            'postal_code': 'S500',
            'phone': '+268 2406 0005',
            'email': 'nhlangano@retail.com',
            'store_type': 'retail',
            'opening_date': '2022-01-12',
        },
        {
            'name': 'Lobamba Warehouse',
            'address': '987 Storage Complex',
            'city': 'Lobamba',
            'region': 'Hhohho',
            'postal_code': 'H600',
            'phone': '+268 2406 0006',
            'email': 'lobamba@retail.com',
            'store_type': 'warehouse',
            'opening_date': '2022-04-18',
        },
    ]

    for data in store_data:
        store = Store.objects.create(**data)
        stores.append(store)
        print(f"Created store: {store.name}")

    return stores

def create_departments(stores):
    """Create departments for each store"""
    departments = []
    department_names = ['Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books']

    for store in stores:
        for dept_name in department_names:
            department, created = Department.objects.get_or_create(
                department_name=dept_name,
                store=store,
                defaults={'description': f'{dept_name} department at {store.name}'}
            )
            departments.append(department)
            if created:
                print(f"Created department: {department.department_name} at {store.name}")
            else:
                print(f"Department already exists: {department.department_name} at {store.name}")

    return departments

def create_employees(stores, departments):
    """Create sample employees"""
    employees = []

    # Get all departments grouped by store
    store_departments = {}
    for dept in departments:
        if dept.store not in store_departments:
            store_departments[dept.store] = []
        store_departments[dept.store].append(dept)

    employee_count = 0
    for store in stores:
        # Create 25-30 employees per store
        num_employees = random.randint(25, 30)
        store_depts = store_departments[store]

        for i in range(num_employees):
            employee_count += 1
            dept = random.choice(store_depts)

            employee = Employee.objects.create(
                first_name=f'First{employee_count}',
                last_name=f'Last{employee_count}',
                email=f'employee{employee_count}@example.com',
                phone=f'+555123456{employee_count:03d}',
                position=f'Position {employee_count}',
                department=dept,  # Now using Department instance
                salary=random.randint(30000, 100000),
                hire_date='2023-01-01',
                is_active=True,
                username=f'employee{employee_count}',
                store=store,
            )
            employees.append(employee)

    print(f"Created {len(employees)} employees")
    return employees

def create_brands_and_categories():
    """Create sample brands and categories"""
    brands = []
    categories = []

    brand_names = ['Samsung', 'Nike', 'Apple', 'Sony', 'Adidas', 'LG', 'Puma', 'Microsoft', 'Dell', 'HP']
    category_names = ['Electronics', 'Clothing', 'Home Appliances', 'Sports', 'Books', 'Furniture', 'Toys', 'Beauty', 'Automotive', 'Garden']

    for name in brand_names:
        brand = Brand.objects.create(name=name)
        brands.append(brand)

    for name in category_names:
        category = Category.objects.create(name=name)
        categories.append(category)

    print(f"Created {len(brands)} brands and {len(categories)} categories")
    return brands, categories

def create_products(suppliers, brands, categories):
    """Create sample products"""
    products = []

    product_templates = [
        {'name': 'Wireless Headphones', 'category': 'Electronics', 'brand': 'Sony', 'price': 299.99},
        {'name': 'Running Shoes', 'category': 'Sports', 'brand': 'Nike', 'price': 149.99},
        {'name': 'Smartphone', 'category': 'Electronics', 'brand': 'Samsung', 'price': 899.99},
        {'name': 'Laptop', 'category': 'Electronics', 'brand': 'Dell', 'price': 1299.99},
        {'name': 'T-Shirt', 'category': 'Clothing', 'brand': 'Adidas', 'price': 29.99},
        {'name': 'Refrigerator', 'category': 'Home Appliances', 'brand': 'LG', 'price': 799.99},
        {'name': 'Basketball', 'category': 'Sports', 'brand': 'Nike', 'price': 49.99},
        {'name': 'Novel Book', 'category': 'Books', 'brand': 'Generic', 'price': 19.99},
        {'name': 'Garden Hose', 'category': 'Garden', 'brand': 'Generic', 'price': 39.99},
        {'name': 'Coffee Maker', 'category': 'Home Appliances', 'brand': 'Generic', 'price': 89.99},
    ]

    for i in range(100):
        template = random.choice(product_templates)
        category = random.choice([c for c in categories if c.name == template['category']])
        brand = random.choice([b for b in brands if b.name == template['brand']] or brands)

        product = Product.objects.create(
            name=f"{template['name']} {i+1}",
            description=f"Description for {template['name']} {i+1}",
            category=category,
            brand=brand,
            unit_price=Decimal(str(random.uniform(10.0, 500.0))).quantize(Decimal('0.01')),
            reorder_level=random.randint(5, 50),
            default_supplier=random.choice(suppliers),
            show_online=True,
            is_active=True,
        )
        products.append(product)

    print(f"Created {len(products)} products")
    return products

def main():
    """Main function to populate all data"""
    print("Starting data population...")

    try:
        # Check if suppliers, brands, and categories exist
        suppliers = list(Supplier.objects.all())
        brands = list(Brand.objects.all())
        categories = list(Category.objects.all())

        if not suppliers or not brands or not categories:
            print("Required data (suppliers, brands, categories) not found. Please run the full population script first.")
            return

        # Create products using existing data
        products = create_products(suppliers, brands, categories)

        print("\nProducts added successfully!")
        print(f"Added {len(products)} products")

    except Exception as e:
        print(f"Error during product creation: {e}")
        print("Some products may have been created. Check the database for existing records.")

if __name__ == '__main__':
    main()
