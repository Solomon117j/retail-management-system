import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')

# Setup Django
django.setup()

from store_management.forms import StoreForm

# Test form validation with phone that has letters - should now fail
form = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '78117803abc',  # Contains letters - should fail
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268'
})

print('Test - Phone with letters (should fail):')
print('Is valid:', form.is_valid())
if not form.is_valid():
    print('Errors:', form.errors)
else:
    print('Form is valid!')

# Test with country code that has letters - should now fail
form2 = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '78117803',
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+abc'  # Letters in country code - should fail
})

print('\nTest - Country code with letters (should fail):')
print('Is valid:', form2.is_valid())
if not form2.is_valid():
    print('Errors:', form2.errors)
else:
    print('Form is valid!')

# Test with valid data - should pass
form3 = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '78117803',  # 8 digits
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268'  # 3 digits = 11 total
})

print('\nTest - Valid data (should pass):')
print('Is valid:', form3.is_valid())
if not form3.is_valid():
    print('Errors:', form3.errors)
else:
    print('Form is valid!')
