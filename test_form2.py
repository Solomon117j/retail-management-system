import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')

# Setup Django
django.setup()

from store_management.forms import StoreForm

# Test form validation with invalid phone
form = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '123',  # Invalid phone - too short
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268'
})

print('Test 1 - Invalid phone:')
print('Is valid:', form.is_valid())
if not form.is_valid():
    print('Errors:', form.errors)

# Test form validation with missing required field
form2 = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    # 'phone': '78117803',  # Missing phone
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268'
})

print('\nTest 2 - Missing phone:')
print('Is valid:', form2.is_valid())
if not form2.is_valid():
    print('Errors:', form2.errors)

# Test form validation with invalid postal code
form3 = StoreForm(data={
    'name': 'Test Store',
    'address': '123 Test St',
    'city': 'Test City',
    'region': 'Test Region',
    'phone': '78117803',
    'opening_date': '2023-01-01',
    'store_type': 'retail',
    'status': 'active',
    'country_code': '+268',
    'postal_code': 'AB'  # Invalid - too short
})

print('\nTest 3 - Invalid postal code:')
print('Is valid:', form3.is_valid())
if not form3.is_valid():
    print('Errors:', form3.errors)
