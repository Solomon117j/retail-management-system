
import os
import django
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from accounts.models import User

def check_staff_customers():
    staff_customers = User.objects.filter(is_customer=True, is_staff=True)
    if staff_customers.exists():
        print("Found customers with staff privileges:")
        for customer in staff_customers:
            print(f"  - {customer.username}")
    else:
        print("No customers with staff privileges found.")

if __name__ == "__main__":
    check_staff_customers()