import os
import django
from datetime import date, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from store_management.models import Store

# Sample stores relevant to eSwatini (excluding warehouses)
stores_data = [
    {
        'name': 'Mbabane Retail Store',
        'address': '123 King Mswati III Avenue',
        'city': 'Mbabane',
        'region': 'Hhohho',
        'postal_code': 'H100',
        'phone': '+268 2404 1234',
        'opening_date': date(2020, 5, 15),
        'email': 'mbabane.retail@example.com',
        'store_type': 'retail',
        'store_size': 500.00,
        'description': 'Main retail store in the capital city.',
        'status': 'active',
        'opening_time': time(9, 0),
        'closing_time': time(18, 0),
        'latitude': -26.3167,
        'longitude': 31.1333,
    },
    {
        'name': 'Manzini Flagship Store',
        'address': '456 Mahlanya Street',
        'city': 'Manzini',
        'region': 'Manzini',
        'postal_code': 'M200',
        'phone': '+268 2505 5678',
        'opening_date': date(2019, 8, 20),
        'email': 'manzini.flagship@example.com',
        'store_type': 'flagship',
        'store_size': 800.00,
        'description': 'Flagship store showcasing premium products.',
        'status': 'active',
        'opening_time': time(8, 30),
        'closing_time': time(19, 0),
        'latitude': -26.5000,
        'longitude': 31.3833,
    },
    {
        'name': 'Matsapha Outlet Store',
        'address': '789 Industrial Area Road',
        'city': 'Matsapha',
        'region': 'Manzini',
        'postal_code': 'M300',
        'phone': '+268 2518 9012',
        'opening_date': date(2021, 3, 10),
        'email': 'matsapha.outlet@example.com',
        'store_type': 'outlet',
        'store_size': 300.00,
        'description': 'Outlet store for discounted items.',
        'status': 'active',
        'opening_time': time(10, 0),
        'closing_time': time(17, 0),
        'latitude': -26.4833,
        'longitude': 31.3167,
    },
    {
        'name': 'Nhlangano Franchise',
        'address': '321 Border Road',
        'city': 'Nhlangano',
        'region': 'Shiselweni',
        'postal_code': 'S400',
        'phone': '+268 2204 3456',
        'opening_date': date(2022, 1, 5),
        'email': 'nhlangano.franchise@example.com',
        'store_type': 'franchise',
        'store_size': 400.00,
        'description': 'Franchised store in southern region.',
        'status': 'active',
        'opening_time': time(9, 30),
        'closing_time': time(18, 30),
        'latitude': -27.1167,
        'longitude': 31.2000,
    },
    {
        'name': 'Siteki Pop-up Store',
        'address': '654 Market Square',
        'city': 'Siteki',
        'region': 'Lubombo',
        'postal_code': 'L500',
        'phone': '+268 2343 7890',
        'opening_date': date(2023, 6, 1),
        'email': 'siteki.popup@example.com',
        'store_type': 'pop_up',
        'store_size': 200.00,
        'description': 'Temporary pop-up store for seasonal sales.',
        'status': 'active',
        'opening_time': time(11, 0),
        'closing_time': time(16, 0),
        'latitude': -26.4500,
        'longitude': 31.9500,
    },
]

# Create stores
for data in stores_data:
    store, created = Store.objects.get_or_create(
        name=data['name'],
        defaults=data
    )
    if created:
        print(f"Created store: {store.name}")
    else:
        print(f"Store already exists: {store.name}")

print("Store population complete.")
