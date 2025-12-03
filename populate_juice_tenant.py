import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from tenants.models import Client
from human_resources.models import Employee
from store_management.models import Department

def populate_juice_tenant():
    """
    Populate the juice tenant with basic data.
    """
    try:
        juice_tenant = Client.objects.get(schema_name='juice')
    except Client.DoesNotExist:
        print("Juice tenant not found!")
        return

    with tenant_context(juice_tenant):
        print(f"Populating tenant: {juice_tenant.name}")

        # Create a superuser for the juice tenant
        User = get_user_model()
        if not User.objects.filter(username='juice_admin').exists():
            user = User.objects.create_user(
                username='juice_admin',
                email='admin@juice.localhost',
                password='juice123!',
                first_name='Juice',
                last_name='Admin',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )

            # Create department first
            department, created = Department.objects.get_or_create(
                name='Management',
                defaults={'description': 'Management Department'}
            )

            # Create Employee profile
            Employee.objects.create(
                user=user,
                employee_id='JUICE001',
                department=department,
                position='Administrator',
                hire_date=datetime.now().date(),
                salary=50000.00,
                is_active=True
            )

            print(f"Created superuser: {user.username} for juice tenant")
        else:
            print("Juice admin user already exists")

        print("Juice tenant populated successfully!")

if __name__ == '__main__':
    populate_juice_tenant()
