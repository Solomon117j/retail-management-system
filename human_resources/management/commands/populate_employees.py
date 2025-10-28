import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import date
from human_resources.models import Employee
from store_management.models import Store, Department


class Command(BaseCommand):
    help = 'Populate the database with sample Swati employees for system login'

    # Sample Swati employee data
    swati_employees = [
        {
            'first_name': 'Sipho',
            'last_name': 'Dlamini',
            'email': 'sipho.dlamini@swati-retail.sz',
            'username': 'sipho.dlamini',
            'position': 'Store Manager',
            'department_name': 'Management',
            'phone': '+268 2406 1234',
            'hire_date': date(2023, 1, 15),
            'salary': 25000.00,
            'role_group': 'Role: Store Manager',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Nomsa',
            'last_name': 'Nkosi',
            'email': 'nomsa.nkosi@swati-retail.sz',
            'username': 'nomsa.nkosi',
            'position': 'Assistant Manager',
            'department_name': 'Management',
            'phone': '+268 2406 1235',
            'hire_date': date(2023, 2, 1),
            'salary': 18000.00,
            'role_group': 'Role: Assistant Manager',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Thabo',
            'last_name': 'Mthembu',
            'email': 'thabo.mthembu@swati-retail.sz',
            'username': 'thabo.mthembu',
            'position': 'Sales Associate',
            'department_name': 'Sales',
            'phone': '+268 2406 1236',
            'hire_date': date(2023, 3, 10),
            'salary': 8500.00,
            'role_group': 'Role: Sales Associate',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Zanele',
            'last_name': 'Shongwe',
            'email': 'zanele.shongwe@swati-retail.sz',
            'username': 'zanele.shongwe',
            'position': 'Sales Associate',
            'department_name': 'Sales',
            'phone': '+268 2406 1237',
            'hire_date': date(2023, 3, 15),
            'salary': 8500.00,
            'role_group': 'Role: Sales Associate',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Bongani',
            'last_name': 'Ndlovu',
            'email': 'bongani.ndlovu@swati-retail.sz',
            'username': 'bongani.ndlovu',
            'position': 'Inventory Supervisor',
            'department_name': 'Inventory',
            'phone': '+268 2406 1238',
            'hire_date': date(2023, 4, 1),
            'salary': 12000.00,
            'role_group': 'Role: Inventory Supervisor',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Phumlani',
            'last_name': 'Mkhize',
            'email': 'phumlani.mkhize@swati-retail.sz',
            'username': 'phumlani.mkhize',
            'position': 'Procurement Specialist',
            'department_name': 'Procurement',
            'phone': '+268 2406 1239',
            'hire_date': date(2023, 4, 15),
            'salary': 14000.00,
            'role_group': 'Role: Procurement Specialist',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Lindiwe',
            'last_name': 'Zulu',
            'email': 'lindiwe.zulu@swati-retail.sz',
            'username': 'lindiwe.zulu',
            'position': 'HR Coordinator',
            'department_name': 'Human Resources',
            'phone': '+268 2406 1240',
            'hire_date': date(2023, 5, 1),
            'salary': 13000.00,
            'role_group': 'Role: HR Coordinator',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Jabulani',
            'last_name': 'Khumalo',
            'email': 'jabulani.khumalo@swati-retail.sz',
            'username': 'jabulani.khumalo',
            'position': 'E-Commerce Manager',
            'department_name': 'E-Commerce',
            'phone': '+268 2406 1241',
            'hire_date': date(2023, 5, 15),
            'salary': 16000.00,
            'role_group': 'Role: E-Commerce Manager',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Thembi',
            'last_name': 'Sithole',
            'email': 'thembi.sithole@swati-retail.sz',
            'username': 'thembi.sithole',
            'position': 'Financial Analyst',
            'department_name': 'Finance',
            'phone': '+268 2406 1242',
            'hire_date': date(2023, 6, 1),
            'salary': 17000.00,
            'role_group': 'Role: Financial Analyst',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'first_name': 'Mandla',
            'last_name': 'Moyo',
            'email': 'mandla.moyo@swati-retail.sz',
            'username': 'mandla.moyo',
            'position': 'System Administrator',
            'department_name': 'IT',
            'phone': '+268 2406 1243',
            'hire_date': date(2023, 6, 15),
            'salary': 20000.00,
            'role_group': 'Role: System Administrator',
            'is_staff': True,
            'is_superuser': False,
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--store-name',
            type=str,
            default='Swati Main Store',
            help='Name of the store to assign employees to',
        )
        parser.add_argument(
            '--create-departments',
            action='store_true',
            help='Create departments if they do not exist',
        )
        parser.add_argument(
            '--default-password',
            type=str,
            default='Swati@2024!',
            help='Default password for all employees',
        )

    def handle(self, *args, **options):
        store_name = options['store_name']
        create_departments = options['create_departments']
        default_password = options['default_password']

        # Get or create the store
        try:
            store = Store.objects.get(name=store_name)
            self.stdout.write(
                self.style.SUCCESS(f'Found store: {store.name} ({store.store_number})')
            )
        except Store.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Store "{store_name}" not found. Please create it first.')
            )
            return

        # Create departments if requested
        if create_departments:
            self.create_departments_for_store(store)

        # Create employees
        created_count = 0
        for employee_data in self.swati_employees:
            try:
                employee = self.create_employee(employee_data, store, default_password)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created employee: {employee.get_full_name()} '
                        f'({employee.username}) - {employee.position}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to create employee {employee_data["username"]}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} employees')
        )

        # Display login information
        self.display_login_info()

    def create_departments_for_store(self, store):
        """Create standard departments for the store"""
        departments = [
            'Management',
            'Sales',
            'Inventory',
            'Procurement',
            'Human Resources',
            'E-Commerce',
            'Finance',
            'IT',
        ]

        for dept_name in departments:
            department, created = Department.objects.get_or_create(
                store=store,
                department_name=dept_name,
                defaults={'description': f'{dept_name} Department'}
            )
            if created:
                self.stdout.write(f'Created department: {dept_name}')
            else:
                self.stdout.write(f'Department already exists: {dept_name}')

    def create_employee(self, employee_data, store, default_password):
        """Create a single employee with all necessary data"""

        # Get or create department
        try:
            department = Department.objects.get(
                store=store,
                department_name=employee_data['department_name']
            )
        except Department.DoesNotExist:
            # Create department if it doesn't exist
            department = Department.objects.create(
                store=store,
                department_name=employee_data['department_name'],
                description=f'{employee_data["department_name"]} Department'
            )
            self.stdout.write(f'Created department: {employee_data["department_name"]}')

        # Create employee
        employee = Employee.objects.create(
            username=employee_data['username'],
            email=employee_data['email'],
            first_name=employee_data['first_name'],
            last_name=employee_data['last_name'],
            position=employee_data['position'],
            phone=employee_data['phone'],
            hire_date=employee_data['hire_date'],
            salary=employee_data['salary'],
            store=store,
            department=department,
            is_staff=employee_data.get('is_staff', True),
            is_superuser=employee_data.get('is_superuser', False),
            is_active=True,
            date_joined=timezone.now(),
        )

        # Set password
        employee.set_password(default_password)
        employee.save()

        # Assign role group if it exists
        role_group_name = employee_data.get('role_group')
        if role_group_name:
            try:
                role_group = Group.objects.get(name=role_group_name)
                employee.groups.add(role_group)
                self.stdout.write(f'  Assigned role: {role_group_name}')
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  Role group not found: {role_group_name}')
                )

        return employee

    def display_login_info(self):
        """Display login information for created employees"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('EMPLOYEE LOGIN CREDENTIALS'))
        self.stdout.write('='*60)

        for employee_data in self.swati_employees:
            self.stdout.write(f'Username: {employee_data["username"]}')
            self.stdout.write(f'Password: Swati@2024! (default)')
            self.stdout.write(f'Position: {employee_data["position"]}')
            self.stdout.write(f'Email: {employee_data["email"]}')
            self.stdout.write('-'*40)

        self.stdout.write(self.style.WARNING(
            '\nREMINDER: Please change default passwords after first login!'
        ))
        self.stdout.write(self.style.WARNING(
            'Run: python manage.py setup_permissions --create-roles'
        ))
        self.stdout.write(self.style.WARNING(
            'to ensure all role groups are created before running this command.'
        ))
