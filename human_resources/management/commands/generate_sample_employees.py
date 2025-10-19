import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from human_resources.models import Employee
from store_management.models import Department, Store


class Command(BaseCommand):
    help = 'Generate sample data for 30 employees with Swati names based on Employee model fields'

    def handle(self, *args, **options):
        # Predefined Swati names (common in Eswatini)
        first_names = [
            'Sipho', 'Thandi', 'Nkosi', 'Zanele', 'Bongani', 'Nomsa', 'Jabulani', 'Thembi',
            'Sibusiso', 'Nomvula', 'Mthokozisi', 'Nothando', 'Sandile', 'Phumzile', 'Vusi',
            'Lindiwe', 'Mzwandile', 'Nokuthula', 'Thulani', 'Zodwa', 'Bhekisisa', 'Gugu',
            'Khumbulani', 'Ntombi', 'Sifiso', 'Zinhle', 'Andile', 'Busisiwe', 'Dumisani',
            'Fikile', 'Gcobani', 'Hlengiwe', 'Jonga', 'Khethiwe', 'Lukhanyo', 'Mfanafuthi',
            'Ncedo', 'Phindile', 'Qinisela', 'Rethabile', 'Sibonelo', 'Thobeka', 'Velaphi',
            'Wandile', 'Xolani', 'Yolanda', 'Zibuyile'
        ]
        last_names = [
            'Dlamini', 'Nkosi', 'Mthembu', 'Shongwe', 'Mdluli', 'Ndlovu', 'Mkhwanazi',
            'Khumalo', 'Sibiya', 'Moyo', 'Ncube', 'Gumede', 'Zulu', 'Buthelezi', 'Cele',
            'Nxumalo', 'Vilakazi', 'Mthethwa', 'Ngwenya', 'Maphalala', 'Sithole', 'Mabuza',
            'Mkhize', 'Magagula', 'Masuku', 'Mahlangu', 'Mthembu', 'Nkomo', 'Tshabalala',
            'Zwane', 'Malinga', 'Mthembu', 'Ndlovu', 'Shabalala', 'Vilakazi', 'Zwane'
        ]

        # Other predefined lists
        cities = ['Mbabane', 'Manzini', 'Lobamba', 'Siteki', 'Piggs Peak', 'Nhlangano', 'Mhlume', 'Big Bend']
        positions = ['Manager', 'Sales Associate', 'Cashier', 'Stock Clerk', 'Supervisor', 'Cleaner', 'Security Guard', 'IT Support', 'Accountant', 'HR Assistant']
        employment_types = ['full_time', 'part_time', 'contract', 'temporary', 'intern']
        genders = ['male', 'female', 'other']
        marital_statuses = ['single', 'married', 'divorced', 'widowed', 'separated']
        languages = ['English', 'siSwati', 'Zulu', 'Xhosa', 'Afrikaans']
        banks = ['First National Bank', 'Nedbank', 'Standard Bank', 'ABSA', 'FNB Eswatini']

        # Get existing departments, stores, and employees for FK assignments
        departments = list(Department.objects.all())
        stores = list(Store.objects.all())
        employees = list(Employee.objects.all())  # For manager assignment

        # Sets to track unique fields
        used_emails = set()
        used_employee_ids = set()
        used_national_ids = set()
        used_passport_numbers = set()
        used_tax_ids = set()

        employees_created = 0
        for i in range(1, 31):
            # Generate unique names
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"

            # Generate unique email
            base_email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            email = base_email
            counter = 1
            while email in used_emails:
                email = f"{first_name.lower()}.{last_name.lower()}{i}_{counter}@example.com"
                counter += 1
            used_emails.add(email)

            # Generate unique IDs
            employee_id = f"EMP{random.randint(10000, 99999)}"
            while employee_id in used_employee_ids:
                employee_id = f"EMP{random.randint(10000, 99999)}"
            used_employee_ids.add(employee_id)

            national_id = f"NI{random.randint(100000, 999999)}"
            while national_id in used_national_ids:
                national_id = f"NI{random.randint(100000, 999999)}"
            used_national_ids.add(national_id)

            passport_number = f"PP{random.randint(1000000, 9999999)}"
            while passport_number in used_passport_numbers:
                passport_number = f"PP{random.randint(1000000, 9999999)}"
            used_passport_numbers.add(passport_number)

            tax_id = f"TAX{random.randint(100000, 999999)}"
            while tax_id in used_tax_ids:
                tax_id = f"TAX{random.randint(100000, 999999)}"
            used_tax_ids.add(tax_id)

            # Other fields
            phone = f"+268{random.randint(70000000, 79999999)}"
            date_of_birth = date.today() - timedelta(days=random.randint(7300, 18250))  # 20-50 years ago
            gender = random.choice(genders)
            marital_status = random.choice(marital_statuses)
            nationality = 'Eswatini'
            street_address = f"{random.randint(1, 999)} {random.choice(['Main Road', 'Church Street', 'Independence Ave', 'King Street'])}"
            city = random.choice(cities)
            postal_code = f"H{random.randint(100, 999)}"
            country = 'Eswatini'
            emergency_contact_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            emergency_contact_phone = f"+268{random.randint(70000000, 79999999)}"
            emergency_contact_relationship = random.choice(['Parent', 'Sibling', 'Spouse', 'Friend', 'Child'])
            hire_date = date.today() - timedelta(days=random.randint(365, 3650))  # 1-10 years ago
            position = random.choice(positions)
            employment_type = random.choice(employment_types)
            contract_end_date = hire_date + timedelta(days=random.randint(365, 1825)) if employment_type == 'contract' else None
            probation_end_date = hire_date + timedelta(days=90) if random.choice([True, False]) else None
            work_schedule = random.choice(['9-5', '8-4', '10-6', 'Flexible']) if random.choice([True, False]) else None
            salary = round(random.uniform(5000, 25000), 2) if random.choice([True, False]) else None
            bank_name = random.choice(banks) if random.choice([True, False]) else None
            account_number = f"{random.randint(1000000000, 9999999999)}" if bank_name else None
            branch_code = f"{random.randint(100000, 999999)}" if bank_name else None
            qualifications = random.choice(['High School Diploma', 'Bachelor\'s Degree', 'Diploma in Business', 'Certificate in Retail', None])
            skills = random.choice(['Customer Service', 'Inventory Management', 'Sales', 'Leadership', None])
            languages_spoken = ', '.join(random.sample(languages, random.randint(1, 3)))
            performance_rating = round(random.uniform(1.0, 5.0), 1) if random.choice([True, False]) else None

            # FK assignments
            department = random.choice(departments) if departments else None
            store = random.choice(stores) if stores else None
            manager = random.choice(employees) if employees and random.choice([True, False]) else None

            # Create the employee
            employee = Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                date_of_birth=date_of_birth,
                gender=gender,
                marital_status=marital_status,
                nationality=nationality,
                street_address=street_address,
                city=city,
                postal_code=postal_code,
                country=country,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_contact_phone,
                emergency_contact_relationship=emergency_contact_relationship,
                employee_id=employee_id,
                national_id=national_id,
                passport_number=passport_number,
                tax_id=tax_id,
                hire_date=hire_date,
                position=position,
                employment_type=employment_type,
                contract_end_date=contract_end_date,
                probation_end_date=probation_end_date,
                work_schedule=work_schedule,
                salary=salary,
                bank_name=bank_name,
                account_number=account_number,
                branch_code=branch_code,
                qualifications=qualifications,
                skills=skills,
                languages_spoken=languages_spoken,
                performance_rating=performance_rating,
                department=department,
                store=store,
                manager=manager,
            )

            # Set a default password
            employee.password = make_password('password123')
            employee.save()

            employees_created += 1
            self.stdout.write(self.style.SUCCESS(f'Created employee: {employee.get_full_name()}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {employees_created} sample employees.'))
