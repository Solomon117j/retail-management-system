import random
from django.core.management.base import BaseCommand
from store_management.models import Department, Store


class Command(BaseCommand):
    help = 'Generate sample departments for existing stores'

    def handle(self, *args, **options):
        # Predefined department names and descriptions
        department_data = [
            {
                'name': 'Sales',
                'description': 'Handles customer sales transactions and product recommendations'
            },
            {
                'name': 'Customer Service',
                'description': 'Manages customer inquiries, complaints, and support services'
            },
            {
                'name': 'Inventory Management',
                'description': 'Oversees stock levels, ordering, and inventory control'
            },
            {
                'name': 'Administration',
                'description': 'Handles administrative tasks, documentation, and office management'
            },
            {
                'name': 'Security',
                'description': 'Ensures store security, safety, and loss prevention'
            },
            {
                'name': 'Maintenance',
                'description': 'Manages store maintenance, repairs, and facilities'
            },
            {
                'name': 'Human Resources',
                'description': 'Handles employee relations, training, and HR matters'
            },
            {
                'name': 'Finance',
                'description': 'Manages financial transactions, budgeting, and accounting'
            },
            {
                'name': 'Marketing',
                'description': 'Handles promotions, advertising, and customer engagement'
            },
            {
                'name': 'Operations',
                'description': 'Oversees daily operations and store management'
            },
            {
                'name': 'Ecommerce',
                'description': 'Manages online sales, digital marketing, and e-commerce platforms'
            },
            {
                'name': 'Procurement',
                'description': 'Handles purchasing, supplier relations, and procurement processes'
            },
            {
                'name': 'Data Analysis',
                'description': 'Analyzes business data, generates reports, and provides insights'
            },
            {
                'name': 'IT Support',
                'description': 'Provides technical support, system maintenance, and IT services'
            },
            {
                'name': 'Manager',
                'description': 'Oversees store operations, manages teams, and handles strategic decisions'
            }
        ]

        # Get all existing stores
        stores = list(Store.objects.all())

        if not stores:
            self.stdout.write(
                self.style.WARNING('No stores found. Please run generate_sample_stores first.')
            )
            return

        departments_created = 0

        # For each store, create a random selection of departments
        for store in stores:
            # Randomly select 3-6 departments for each store
            num_departments = random.randint(3, 6)
            selected_departments = random.sample(department_data, num_departments)

            for dept_data in selected_departments:
                # Check if department already exists for this store
                existing_dept = Department.objects.filter(
                    store=store,
                    department_name=dept_data['name']
                ).first()

                if existing_dept:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Department '{dept_data['name']}' already exists for store '{store.name}'"
                        )
                    )
                    continue

                # Create the department
                department = Department.objects.create(
                    department_name=dept_data['name'],
                    description=dept_data['description'],
                    store=store
                )

                departments_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created department: {department.department_name} for {store.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {departments_created} sample departments across {len(stores)} stores.'
            )
        )
