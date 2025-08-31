#!/usr/bin/env python
"""
Script to create test staff users for the retail management system.
Run this script to ensure test users exist with proper credentials.
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

from django.contrib.auth import get_user_model
from accounts.models import Employee

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

User = get_user_model()

def create_test_staff_user(username, password, email=None, department='Unassigned'):
    """Create a test staff user with proper attributes"""
    if email is None:
        email = f"{username}@example.com"
    
    try:
        # Check if user already exists
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_employee': True,
                'is_active': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            logger.info(f"✅ Created user: {username} with password: {password}")
        else:
            # Update existing user if needed
            if not user.is_staff:
                user.is_staff = True
            if not user.is_employee:
                user.is_employee = True
            if not user.is_active:
                user.is_active = True
            user.set_password(password)
            user.save()
            logger.info(f"✅ Updated user: {username} with correct attributes")
        
        # Ensure employee profile exists
        if not hasattr(user, 'employee_profile'):
            Employee.objects.create(user=user, department=department)
            logger.info(f"✅ Created employee profile for {username} in department: {department}")
        else:
            # Update department if needed
            if user.employee_profile.department != department:
                user.employee_profile.department = department
                user.employee_profile.save()
                logger.info(f"✅ Updated department for {username} to: {department}")
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Error creating user {username}: {e}")
        return None

def main():
    """Create standard test staff users"""
    logger.info("=" * 60)
    logger.info("CREATING TEST STAFF USERS")
    logger.info("=" * 60)
    
    # Standard test staff users
    test_users = [
        {'username': 'teststaff', 'password': 'testpass123', 'department': 'Management'},
        {'username': 'teststaff2', 'password': 'testpass123', 'department': 'Sales'},
        {'username': 'teststaff3', 'password': 'testpass123', 'department': 'Operations'},
        {'username': 'admin', 'password': 'admin123', 'department': 'Administration'},
    ]
    
    for user_info in test_users:
        create_test_staff_user(**user_info)
    
    logger.info("=" * 60)
    logger.info("TEST USERS READY FOR LOGIN")
    logger.info("=" * 60)
    logger.info("Use these credentials to test staff login:")
    for user_info in test_users:
        logger.info(f"  Username: {user_info['username']}")
        logger.info(f"  Password: {user_info['password']}")
        logger.info(f"  Department: {user_info['department']}")
        logger.info("  " + "-" * 40)
    
    logger.info("Login URL: /accounts/login/staff/")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
