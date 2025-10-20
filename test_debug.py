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

print('Phone value:', repr(form.data.get('phone')))
print('Country code value:', repr(form.data.get('country_code')))
print('Phone is digit?', form.data.get('phone').isdigit())
print('Country code clean:', repr(form.data.get('country_code').lstrip('+')))
print('Country code clean is digit?', form.data.get('country_code').lstrip('+').isdigit())

# Call full_clean to trigger validation
form.full_clean()

print('Cleaned data phone:', repr(form.cleaned_data.get('phone')))
print('Cleaned data country_code:', repr(form.cleaned_data.get('country_code')))

print('Is valid:', form.is_valid())
if not form.is_valid():
    print('Errors:', form.errors)
else:
    print('Form is valid!')
