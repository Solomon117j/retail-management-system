import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')

# Setup Django
django.setup()

from store_management.forms import StoreForm

# Test form validation with phone that doesn't make 11 digits total
form = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '78117803',  # 8 digits
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268'  # 3 digits
})

print('Test - Phone validation (8 + 3 = 11 digits):')
print('Is valid:', form.is_valid())
if not form.is_valid():
    print('Errors:', form.errors)
else:
    print('Form is valid!')

# Test with 9 digit phone
form2 = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '781178039',  # 9 digits
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268'  # 3 digits = 12 total
})

print('\nTest - Phone validation (9 + 3 = 12 digits - should fail):')
print('Is valid:', form2.is_valid())
if not form2.is_valid():
    print('Errors:', form2.errors)
else:
    print('Form is valid!')
