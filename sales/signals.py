import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Customer
from e_commerce.models import CustomerAccount

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomerAccount)
def sync_customer_account_to_customer(sender, instance, created, **kwargs):
    """
    When a CustomerAccount is created or updated, sync with Customer model
    """
    try:
        if created:
            # Check if Customer already exists with this email
            existing_customer = Customer.objects.filter(email=instance.email).first()

            if existing_customer:
                # Link existing Customer to this CustomerAccount
                existing_customer.customer_account = instance
                existing_customer.save()
                logger.info(f"Linked existing Customer {existing_customer} to CustomerAccount {instance}")
            else:
                # Create new Customer record
                customer = Customer.objects.create(
                    customer_account=instance,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    email=instance.email,
                    phone=instance.phone,
                    address=instance.address,
                    join_date=instance.date_joined.date() if instance.date_joined else timezone.now().date(),
                    loyalty_points=instance.loyalty_points
                )
                logger.info(f"Created Customer {customer} from CustomerAccount {instance}")
        else:
            # Update existing Customer record
            if hasattr(instance, 'sales_customer') and instance.sales_customer:
                customer = instance.sales_customer
                customer.first_name = instance.first_name
                customer.last_name = instance.last_name
                customer.email = instance.email
                customer.phone = instance.phone
                customer.address = instance.address
                customer.loyalty_points = instance.loyalty_points
                customer.save()
                logger.info(f"Updated Customer {customer} from CustomerAccount {instance}")

    except Exception as e:
        logger.error(f"Error syncing CustomerAccount to Customer: {e}")

@receiver(post_save, sender=Customer)
def sync_customer_to_customer_account(sender, instance, created, **kwargs):
    """
    When a Customer is created or updated, sync with CustomerAccount model
    """
    try:
        if created and not instance.customer_account:
            # Check if CustomerAccount already exists with this email
            existing_account = CustomerAccount.objects.filter(email=instance.email).first()

            if existing_account:
                # Link existing CustomerAccount to this Customer
                instance.customer_account = existing_account
                instance.save()
                logger.info(f"Linked existing CustomerAccount {existing_account} to Customer {instance}")
            else:
                # Create new CustomerAccount record
                from django.contrib.auth import get_user_model
                User = get_user_model()

                # Create a user account for the customer
                username = f"{instance.first_name.lower()}.{instance.last_name.lower()}"
                # Ensure unique username
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1

                user = User.objects.create_user(
                    username=username,
                    email=instance.email,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    is_customer=True,
                    is_employee=False
                )

                # Create CustomerAccount
                account = CustomerAccount.objects.create(
                    user=user,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    email=instance.email,
                    phone=instance.phone,
                    address=instance.address,
                    loyalty_points=instance.loyalty_points
                )

                # Link back to Customer
                instance.customer_account = account
                instance.save()
                logger.info(f"Created CustomerAccount {account} from Customer {instance}")
        elif not created and instance.customer_account:
            # Update existing CustomerAccount record
            account = instance.customer_account
            account.first_name = instance.first_name
            account.last_name = instance.last_name
            account.email = instance.email
            account.phone = instance.phone
            account.address = instance.address
            account.loyalty_points = instance.loyalty_points
            account.save()
            logger.info(f"Updated CustomerAccount {account} from Customer {instance}")

    except Exception as e:
        logger.error(f"Error syncing Customer to CustomerAccount: {e}")
