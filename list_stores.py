import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from store_management.models import Store

# Get stores excluding warehouses
stores = Store.objects.exclude(store_type='warehouse')

print('List of stores (excluding warehouses):')
for store in stores:
    print(f'{store.name} - {store.store_type}')
