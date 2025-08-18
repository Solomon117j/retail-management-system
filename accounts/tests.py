# accounts/tests.py
import logging
from django.test import TestCase
from .models import User

logger = logging.getLogger(__name__)

class ProfileCreationTests(TestCase):
    def test_employee_profile_creation(self):
        """Test Employee profile is automatically created for new employees"""
        logger.info("Starting test_employee_profile_creation")
        
        # Create a user with is_employee=True
        user = User.objects.create_user(
            username='john',
            password='testpass123',
            is_employee=True
        )
        logger.info(f"User created: {user.username}, is_employee={user.is_employee}")
        
        # Check database directly
        from .models import Employee
        employee_count = Employee.objects.count()
        logger.info(f"Total employees in DB: {employee_count}")
        
        if employee_count > 0:
            employee = Employee.objects.first()
            logger.info(f"First employee: user={employee.user.username}, dept={employee.department}")
        
        user.refresh_from_db()
        
        # Check for employee_profile attribute
        has_profile = hasattr(user, 'employee_profile')
        logger.info(f"User has employee_profile attribute? {has_profile}")
        
        if has_profile:
            logger.info(f"Employee profile: {user.employee_profile}")
        
        self.assertTrue(has_profile, "employee_profile attribute missing")

    def test_customer_profile_creation(self):
        """Test Customer profile is automatically created for new customers"""
        logger.info("Starting test_customer_profile_creation")
        
        user = User.objects.create_user(
            username='customer1',
            password='testpass123',
            is_customer=True
        )
        logger.info(f"User created: {user.username}, is_customer={user.is_customer}")
        
        # Check customer profile
        self.assertTrue(user.customer_set.exists())
        customer = user.customer_set.first()
        self.assertEqual(customer.loyalty_points, 0)
        logger.info(f"Customer created with loyalty points: {customer.loyalty_points}")

    def test_employee_profile_removal(self):
        """Test Employee profile is removed when is_employee set to False"""
        logger.info("Starting test_employee_profile_removal")
        
        # Create employee user
        user = User.objects.create_user(
            username='test_employee_removal',
            password='testpass123',
            is_employee=True
        )
        self.assertTrue(hasattr(user, 'employee_profile'))
        logger.info(f"Created employee user with profile")
        
        # Remove employee status
        user.is_employee = False
        user.save()
        logger.info(f"Set is_employee=False and saved user")
        
        # Verify profile removal
        user.refresh_from_db()
        self.assertFalse(hasattr(user, 'employee_profile'))
        logger.info(f"Verified employee profile was removed")

    def test_customer_profile_removal(self):
        """Test Customer profile is removed when is_customer set to False"""
        logger.info("Starting test_customer_profile_removal")
        
        # Create customer user
        user = User.objects.create_user(
            username='test_customer_removal',
            password='testpass123',
            is_customer=True
        )
        self.assertEqual(user.customer_set.count(), 1)
        logger.info(f"Created customer user with profile")
        
        # Remove customer status
        user.is_customer = False
        user.save()
        logger.info(f"Set is_customer=False and saved user")
        
        # Verify profile removal
        self.assertEqual(user.customer_set.count(), 0)
        logger.info(f"Verified customer profile was removed")