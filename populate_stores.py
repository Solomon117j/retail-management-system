#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from store_management.models import Store

def populate_stores():
    """Create some test stores"""
    from datetime import date
    stores_data = [
        {
            'store_name': 'Main Store',
            'address': '123 Main Street',
            'city': 'Mbabane',
            'region': 'Hhohho',
            'phone': '+268 2400 0000',
            'opening_date': date.today(),
        },
        {
            'store_name': 'Branch Store',
            'address': '456 Branch Avenue',
            'city': 'Manzini',
            'region': 'Manzini',
            'phone': '+268 2500 0000',
            'opening_date': date.today(),
        },
        {
            'store_name': 'Outlet Store',
            'address': '789 Outlet Road',
            'city': 'Siteki',
            'region': 'Lubombo',
            'phone': '+268 2600 0000',
            'opening_date': date.today(),
        },
    ]

    created_count = 0
    for store_data in stores_data:
        store, created = Store.objects.get_or_create(
            store_name=store_data['store_name'],
            defaults=store_data
        )
        if created:
            created_count += 1
            print(f"Created store: {store.store_name}")

    print(f"Stores: {created_count} created, {Store.objects.count()} total")

if __name__ == '__main__':
    print("Populating stores...")
    populate_stores()
    print("Done!")
