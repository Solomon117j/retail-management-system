#!/usr/bin/env python
import os
import django
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from human_resources.models import Employee

def create_test_data():
    # Create a manager
    manager = Employee.objects.create(
        first_name='Vusi',
        last_name='Dlamini',
        email='vusi.dlamini@example.com',
        username='mavusana',
        position='Manager',
        is_active=True
    )
    print(f"Created manager: {manager.get_full_name()}")

    # Create subordinates
    for i in range(5):
        subordinate = Employee.objects.create(
            first_name=f'Subordinate {i+1}',
            last_name='Test',
            email=f'subordinate{i+1}@example.com',
            username=f'subordinate{i+1}',
            position='Employee',
            manager=manager,  # Assign the manager
            is_active=True
        )
        print(f"Created subordinate: {subordinate.get_full_name()}")

if __name__ == "__main__":
    create_test_data()
