import os
import django
import sys
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
import logging

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

User = get_user_model()

class CustomerLoginTest(TestCase):
    def setUp(self):
        # Create a test customer user
        self.user = User.objects.create_user(
            username='testcustomer',
            password='testpass123',
            email='test@example.com',
            is_customer=True
        )

    def test_customer_login(self):
        client = Client()
        response = client.post('/accounts/login/customer/', {
            'username': 'testcustomer',
            'password': 'testpass123'
        }, follow=True)

        # Check if the login was successful
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, '/e_commerce/customer-accounts/')

if __name__ == "__main__":
    CustomerLoginTest().test_customer_login()
