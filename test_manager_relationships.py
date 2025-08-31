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

def test_manager_relationships():
    print("Testing Manager-Subordinate Relationships")
    print("=" * 50)
    
    # Count total employees
    total_employees = Employee.objects.count()
    print(f"Total employees: {total_employees}")
    
    # Find managers
    managers = Employee.objects.filter(position__icontains='manager')
    print(f"Managers found: {managers.count()}")
    
    if managers.exists():
        print("\nManager Details:")
        print("-" * 30)
        for manager in managers[:5]:  # Show first 5 managers
            subordinates_count = Employee.objects.filter(manager=manager).count()
            print(f"Manager: {manager.get_full_name()} (ID: {manager.pk})")
            print(f"  Position: {manager.position}")
            print(f"  Subordinates: {subordinates_count}")
            
            if subordinates_count > 0:
                subordinates = Employee.objects.filter(manager=manager)[:3]  # Show first 3 subordinates
                for sub in subordinates:
                    print(f"    - {sub.get_full_name()} (ID: {sub.pk})")
            print()
    else:
        print("No managers found in the database.")
    
    # Check if any employees have managers
    employees_with_managers = Employee.objects.filter(manager__isnull=False)
    print(f"Employees with managers: {employees_with_managers.count()}")

if __name__ == "__main__":
    test_manager_relationships()
