import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from e_commerce.models import CustomerAccount

User = get_user_model()

def test_customer_registration():
    client = Client()

    # Test data
    registration_data = {
        'username': 'testuser123',
        'email': 'testuser@example.com',
        'password': 'testpass123',
        'password2': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }

    print("Testing customer registration...")

    # Make POST request to registration endpoint
    response = client.post('/accounts/register/', data=registration_data)

    print(f"Response status code: {response.status_code}")
    print(f"Response URL: {response.url}")

    # Check if user was created
    try:
        user = User.objects.get(username='testuser123')
        print(f"User created: {user.username}, email: {user.email}, is_customer: {user.is_customer}")
    except User.DoesNotExist:
        print("ERROR: User was not created!")
        return False

    # Check if CustomerAccount was created
    try:
        customer_account = CustomerAccount.objects.get(user=user)
        print(f"CustomerAccount created: {customer_account.first_name} {customer_account.last_name}, email: {customer_account.email}")
    except CustomerAccount.DoesNotExist:
        print("ERROR: CustomerAccount was not created!")
        return False

    # Check if user is logged in (session should have user id)
    if '_auth_user_id' in client.session:
        print("User is logged in successfully")
    else:
        print("ERROR: User is not logged in!")

    # Check redirect
    if response.status_code == 302 and 'customer_account_list' in response.url:
        print("Redirect to customer account list successful")
    else:
        print(f"ERROR: Unexpected redirect. Status: {response.status_code}, URL: {response.url}")

    print("Test completed successfully!")
    return True

if __name__ == '__main__':
    test_customer_registration()
