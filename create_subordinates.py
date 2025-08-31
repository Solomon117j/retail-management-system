#!/usr/bin/env python
import os
import django
import sys
import uuid

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from human_resources.models import Employee

def create_subordinates():
    # Get the existing manager
    try:
        manager = Employee.objects.get(username='mavusana')
        print(f"Found manager: {manager.get_full_name()} (ID: {manager.pk})")
    except Employee.DoesNotExist:
        print("Manager not found. Please create a manager first.")
        return
    
    # Create subordinates
    for i in range(5):
        subordinate = Employee.objects.create(
            first_name=f'Subordinate {i+1}',
            last_name='Test',
            email=f'subordinate{i+1}-{uuid.uuid4().hex[:6]}@example.com',
            username=f'subordinate{i+1}-{uuid.uuid4().hex[:6]}',
            position='Employee',
            manager=manager,  # Assign the manager
            is_active=True
        )
        print(f"Created subordinate: {subordinate.get_full_name()}")

if __name__ == "__main__":
    create_subordinates()
