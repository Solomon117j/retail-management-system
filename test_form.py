import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')

# Setup Django
django.setup()

from store_management.forms import StoreForm

# Test form validation
form = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '78117803',
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268'
})

print('Is valid:', form.is_valid())
if not form.is_valid():
    print('Errors:', form.errors)
else:
    print('Form is valid!')
