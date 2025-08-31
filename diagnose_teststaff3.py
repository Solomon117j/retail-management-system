#!/usr/bin/env python
"""
Diagnostic script to check teststaff3 user status and identify login issues.
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

from django.contrib.auth import get_user_model, authenticate
from accounts.models import Employee
from django.db import connection

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

User = get_user_model()

def check_user_exists(username):
    """Check if user exists in database"""
    try:
        user = User.objects.get(username=username)
        logger.info(f"✅ User '{username}' exists in database")
        return user
    except User.DoesNotExist:
        logger.error(f"❌ User '{username}' does not exist in database")
        return None

def check_user_attributes(user):
    """Check user attributes required for staff login"""
    logger.info(f"Checking attributes for user: {user.username}")
    
    # Check is_active
    if user.is_active:
        logger.info(f"✅ User is active: {user.is_active}")
    else:
        logger.error(f"❌ User is NOT active: {user.is_active}")
    
    # Check is_staff
    if user.is_staff:
        logger.info(f"✅ User is staff: {user.is_staff}")
    else:
        logger.error(f"❌ User is NOT staff: {user.is_staff}")
    
    # Check is_employee
    if user.is_employee:
        logger.info(f"✅ User is employee: {user.is_employee}")
    else:
        logger.error(f"❌ User is NOT employee: {user.is_employee}")
    
    return user.is_active and user.is_staff and user.is_employee

def check_employee_profile(user):
    """Check if user has employee profile"""
    try:
        if hasattr(user, 'employee_profile'):
            employee = user.employee_profile
            logger.info(f"✅ Employee profile exists: {employee}")
            logger.info(f"   Department: {employee.department}")
            return True
        else:
            logger.error("❌ Employee profile does NOT exist")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking employee profile: {e}")
        return False

def check_password(user, password):
    """Check if password is correct"""
    authenticated_user = authenticate(username=user.username, password=password)
    if authenticated_user:
        logger.info(f"✅ Password authentication successful")
        return True
    else:
        logger.error(f"❌ Password authentication FAILED")
        return False

def check_database_connection():
    """Check database connection"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def check_all_employees():
    """List all employees in database"""
    try:
        employees = Employee.objects.all()
        logger.info(f"Total employees in database: {employees.count()}")
        for emp in employees:
            logger.info(f"  - {emp.user.username}: {emp.department}")
        return True
    except Exception as e:
        logger.error(f"Error listing employees: {e}")
        return False

def main():
    """Main diagnostic function"""
    logger.info("=" * 60)
    logger.info("DIAGNOSTIC CHECK FOR teststaff3 LOGIN ISSUE")
    logger.info("=" * 60)
    
    # Check database connection
    check_database_connection()
    
    # Check if teststaff3 exists
    user = check_user_exists('teststaff3')
    
    if not user:
        logger.info("Creating teststaff3 user for testing...")
        try:
            user = User.objects.create_user(
                username='teststaff3',
                password='testpass123',
                email='teststaff3@example.com',
                is_staff=True,
                is_employee=True,
                is_active=True
            )
            logger.info(f"✅ Created teststaff3 user with ID: {user.id}")
        except Exception as e:
            logger.error(f"❌ Failed to create teststaff3 user: {e}")
            return
    
    # Check user attributes
    attributes_ok = check_user_attributes(user)
    
    # Check employee profile
    profile_ok = check_employee_profile(user)
    
    # Check password
    password_ok = check_password(user, 'testpass123')
    
    # List all employees
    check_all_employees()
    
    logger.info("=" * 60)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 60)
    
    if attributes_ok and profile_ok and password_ok:
        logger.info("✅ All checks passed - user should be able to login")
    else:
        logger.info("❌ One or more checks failed - login will likely fail")
        
        if not attributes_ok:
            logger.info("  - User attributes are incorrect")
        if not profile_ok:
            logger.info("  - Employee profile is missing")
        if not password_ok:
            logger.info("  - Password authentication failed")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
