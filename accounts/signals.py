import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from accounts.models import Customer, Employee

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def manage_user_profiles(sender, instance, created, **kwargs):
    """Signal handler to create/update/delete related profiles based on user type."""
        
    logger.info(f"User created with is_employee={instance.is_employee} and is_customer={instance.is_customer}, User ID: {instance.id}")
    if instance.is_employee:
        logger.info("Checking for employee profile creation...")
    if instance.is_customer:
        logger.info("Checking for customer profile creation...")
    updated_fields = kwargs.get('update_fields')
    
    # Check if the user instance exists before processing updates
    if not User.objects.filter(id=instance.id).exists():
        logger.error(f"User instance does not exist for ID: {instance.id}")
        return
    
    # If this is an update (not creation) and update_fields is specified
    if not created and updated_fields is not None:
        # Convert to set if it's a tuple or list
        if isinstance(updated_fields, (list, tuple)):
            updated_fields = set(updated_fields)
        
        # Always process profile management if user is being logged in
        if 'is_employee' in updated_fields or 'is_customer' in updated_fields:
            logger.info(f"Processing profile management for user: {instance.username} (updated_fields: {updated_fields})")
        else:
            logger.debug(f"Skipping profile management for {instance.username} - no relevant fields updated in update_fields: {updated_fields}")
            return
    
    # If update_fields is None (full save), we should process profile management
    # This handles the case where user.is_employee or user.is_customer might have changed
    
    logger.info(f"Managing profiles for user: {instance.username} (created: {created}, update_fields: {updated_fields})")

    # Employee profile management
    if instance.is_employee:
        if not hasattr(instance, 'employee_profile'):
            logger.info("Creating employee profile")
            try:
                Employee.objects.create(user=instance, department='Unassigned')
                logger.info("Employee profile created successfully")
            except Exception as e:
                logger.error(f"Error creating employee profile: {e}")
        else:
            logger.debug("Employee profile already exists")
    elif hasattr(instance, 'employee_profile'):
        logger.info("Removing employee profile (is_employee=False)")
        try:
            instance.employee_profile.all().delete()
            logger.info("Employee profile deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting employee profile: {e}")

    # Customer profile management
    if instance.is_customer:
        if not instance.customer_set.exists():
            logger.info("Creating customer profile")
            try:
                Customer.objects.create(user=instance)
                logger.info("Customer profile created successfully")
            except Exception as e:
                logger.error(f"Error creating customer profile: {e}")
        else:
            logger.debug("Customer profile(s) already exist")
    elif instance.customer_set.exists():
        logger.info("Removing customer profile(s) (is_customer=False)")
        try:
            instance.customer_set.all().delete()
            logger.info("Customer profile(s) deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting customer profile(s): {e}")
