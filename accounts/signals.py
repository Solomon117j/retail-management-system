import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Customer, Employee

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def manage_user_profiles(sender, instance, created, **kwargs):
    """
    Automatically creates or deletes user profiles based on role flags
    - Creates Employee profile when is_employee=True and profile doesn't exist
    - Deletes Employee profile when is_employee=False and profile exists
    - Creates Customer profile when is_customer=True and no profile exists
    - Deletes all Customer profiles when is_customer=False and profiles exist
    """
    
    # Handle update_fields being None
    updated_fields = kwargs.get('update_fields', set())
    if not created and updated_fields is not None:
        # Convert to set if it's a tuple or list
        if isinstance(updated_fields, (list, tuple)):
            updated_fields = set(updated_fields)
        
        # Skip if no relevant fields were updated
        if updated_fields and not updated_fields.intersection({'is_employee', 'is_customer'}):
            logger.debug(f"Skipping profile management for {instance.username} - no relevant fields updated")
            return

    logger.info(f"Managing profiles for user: {instance.username}")

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
            instance.employee_profile.delete()
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