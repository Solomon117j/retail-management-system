#!/usr/bin/env python
"""
Test script to verify customer login functionality with the created test users
"""
import os
import sys
import django
import logging

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from e_commerce.models import CustomerAccount

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

User = get_user_model()

def test_customer_login():
    """Test customer login functionality with all test users"""
    logger.info("=" * 60)
    logger.info("TESTING CUSTOMER LOGIN WITH ALL TEST USERS")
    logger.info("=" * 60)
    
    client = Client()
    
    # Test users to verify
    test_users = [
        {'username': 'testcustomer', 'password': 'testpass123'},
        {'username': 'johnsmith', 'password': 'testpass123'},
        {'username': 'janedoe', 'password': 'testpass123'},
        {'username': 'robertjones', 'password': 'testpass123'},
    ]
    
    for user_info in test_users:
        username = user_info['username']
        password = user_info['password']
        
        logger.info(f"\nTesting login for: {username}")
        logger.info("-" * 40)
        
        # Test login with correct credentials
        response = client.post('/accounts/login/customer/', {
            'username': username,
            'password': password
        }, follow=True)
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Redirect chain: {response.redirect_chain}")
        
        # Check if login was successful
        if response.status_code == 200:
            if response.wsgi_request.user.is_authenticated:
                logger.info("✅ LOGIN SUCCESSFUL!")
                logger.info(f"Authenticated user: {response.wsgi_request.user.username}")
                logger.info(f"User is customer: {response.wsgi_request.user.is_customer}")
                
                # Check if CustomerAccount exists
                try:
                    customer_account = CustomerAccount.objects.get(user=response.wsgi_request.user)
                    logger.info(f"CustomerAccount: {customer_account.first_name} {customer_account.last_name}")
                    logger.info(f"Loyalty Points: {customer_account.loyalty_points}")
                except CustomerAccount.DoesNotExist:
                    logger.error("❌ CustomerAccount does not exist")
                
            else:
                logger.error("❌ LOGIN FAILED - User not authenticated")
                
                # Check for error messages
                from django.contrib.messages import get_messages
                messages = list(get_messages(response.wsgi_request))
                for message in messages:
                    logger.error(f"Error message: {message}")
        else:
            logger.error(f"❌ LOGIN FAILED - Status code: {response.status_code}")
        
        # Logout before testing next user
        client.logout()
    
    # Test login with incorrect password
    logger.info("\nTesting with incorrect password...")
    response = client.post('/accounts/login/customer/', {
        'username': 'testcustomer',
        'password': 'wrongpassword'
    }, follow=True)
    
    if response.status_code == 200 and not response.wsgi_request.user.is_authenticated:
        logger.info("✅ Correctly rejected incorrect password")
    else:
        logger.error("❌ Unexpected behavior with incorrect password")
    
    logger.info("=" * 60)
    logger.info("CUSTOMER LOGIN TESTING COMPLETE")
    logger.info("=" * 60)

def list_all_customers():
    """List all customer accounts in the database"""
    logger.info("\nListing all CustomerAccounts:")
    logger.info("-" * 40)
    
    try:
        customers = CustomerAccount.objects.all()
        logger.info(f"Total CustomerAccounts: {customers.count()}")
        
        for customer in customers:
            logger.info(f"  - {customer.first_name} {customer.last_name} ({customer.email})")
            logger.info(f"    Username: {customer.user.username}, Loyalty: {customer.loyalty_points} points")
            logger.info(f"    User ID: {customer.user.id}")
            logger.info("    " + "-" * 30)
            
    except Exception as e:
        logger.error(f"Error listing customers: {e}")

if __name__ == "__main__":
    test_customer_login()
    list_all_customers()
