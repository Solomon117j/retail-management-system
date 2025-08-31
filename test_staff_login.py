#!/usr/bin/env python
"""
Test script to verify staff login functionality with teststaff3/testpass123
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

User = get_user_model()

def test_staff_login():
    """Test staff login functionality"""
    logger.info("=" * 60)
    logger.info("TESTING STAFF LOGIN WITH teststaff3/testpass123")
    logger.info("=" * 60)
    
    client = Client()
    
    # Test login with correct credentials
    logger.info("Attempting login with teststaff3/testpass123...")
    response = client.post('/accounts/login/staff/', {
        'username': 'teststaff3',
        'password': 'testpass123'
    }, follow=True)
    
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Redirect chain: {response.redirect_chain}")
    
    # Check if login was successful
    if response.status_code == 200:
        if response.wsgi_request.user.is_authenticated:
            logger.info("✅ LOGIN SUCCESSFUL!")
            logger.info(f"Authenticated user: {response.wsgi_request.user.username}")
            logger.info(f"User is staff: {response.wsgi_request.user.is_staff}")
            logger.info(f"User is employee: {response.wsgi_request.user.is_employee}")
        else:
            logger.error("❌ LOGIN FAILED - User not authenticated")
            
            # Check for error messages
            from django.contrib.messages import get_messages
            messages = list(get_messages(response.wsgi_request))
            for message in messages:
                logger.error(f"Error message: {message}")
    else:
        logger.error(f"❌ LOGIN FAILED - Status code: {response.status_code}")
    
    # Test login with incorrect password
    logger.info("\nTesting with incorrect password...")
    response = client.post('/accounts/login/staff/', {
        'username': 'teststaff3',
        'password': 'wrongpassword'
    }, follow=True)
    
    if response.status_code == 200 and not response.wsgi_request.user.is_authenticated:
        logger.info("✅ Correctly rejected incorrect password")
    else:
        logger.error("❌ Unexpected behavior with incorrect password")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    test_staff_login()
