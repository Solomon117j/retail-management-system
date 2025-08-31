#!/usr/bin/env python
"""
Script to create test customer users for the retail management system.
Run this script to ensure test customer users exist with proper credentials.
"""
import os
import sys
import django
import logging
from datetime import date, timedelta

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from e_commerce.models import CustomerAccount

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

User = get_user_model()

def create_test_customer_user(username, password, first_name, last_name, email=None, 
                            phone="+1234567890", address="123 Test Street", 
                            birth_date=None, loyalty_points=0):
    """Create a test customer user with proper attributes and CustomerAccount"""
    if email is None:
        email = f"{username}@example.com"
    
    if birth_date is None:
        birth_date = date.today() - timedelta(days=365*25)  # 25 years old
    
    try:
        # Check if user already exists
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_customer': True,
                'is_employee': False,
                'is_active': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            logger.info(f"✅ Created user: {username} with password: {password}")
        else:
            # Update existing user if needed
            if not user.is_customer:
                user.is_customer = True
            if user.is_employee:
                user.is_employee = False
            if not user.is_active:
                user.is_active = True
            user.set_password(password)
            user.save()
            logger.info(f"✅ Updated user: {username} with correct attributes")
        
        # Ensure CustomerAccount exists
        customer_account, ca_created = CustomerAccount.objects.get_or_create(
            user=user,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address': address,
                'birth_date': birth_date,
                'loyalty_points': loyalty_points
            }
        )
        
        if ca_created:
            logger.info(f"✅ Created CustomerAccount for {username}")
        else:
            # Update CustomerAccount if needed
            customer_account.first_name = first_name
            customer_account.last_name = last_name
            customer_account.email = email
            customer_account.phone = phone
            customer_account.address = address
            customer_account.birth_date = birth_date
            customer_account.loyalty_points = loyalty_points
            customer_account.save()
            logger.info(f"✅ Updated CustomerAccount for {username}")
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Error creating customer user {username}: {e}")
        return None

def main():
    """Create standard test customer users"""
    logger.info("=" * 60)
    logger.info("CREATING TEST CUSTOMER USERS")
    logger.info("=" * 60)
    
    # Standard test customer users
    test_customers = [
        {
            'username': 'testcustomer', 
            'password': 'testpass123', 
            'first_name': 'Test',
            'last_name': 'Customer',
            'email': 'testcustomer@example.com',
            'loyalty_points': 100
        },
        {
            'username': 'johnsmith', 
            'password': 'testpass123', 
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@example.com',
            'loyalty_points': 250
        },
        {
            'username': 'janedoe', 
            'password': 'testpass123', 
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'loyalty_points': 500
        },
        {
            'username': 'robertjones', 
            'password': 'testpass123', 
            'first_name': 'Robert',
            'last_name': 'Jones',
            'email': 'robert.jones@example.com',
            'loyalty_points': 50
        },
    ]
    
    for customer_info in test_customers:
        create_test_customer_user(**customer_info)
    
    logger.info("=" * 60)
    logger.info("TEST CUSTOMER USERS READY FOR LOGIN")
    logger.info("=" * 60)
    logger.info("Use these credentials to test customer login:")
    for customer_info in test_customers:
        logger.info(f"  Username: {customer_info['username']}")
        logger.info(f"  Password: {customer_info['password']}")
        logger.info(f"  Name: {customer_info['first_name']} {customer_info['last_name']}")
        logger.info(f"  Loyalty Points: {customer_info['loyalty_points']}")
        logger.info("  " + "-" * 40)
    
    logger.info("Login URL: /accounts/login/customer/")
    logger.info("Redirects to: /e_commerce/customer-accounts/")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
