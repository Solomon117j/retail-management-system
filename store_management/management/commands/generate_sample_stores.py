import random
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from store_management.models import Store, STORE_TYPE_CHOICES, STORE_STATUS_CHOICES
from human_resources.models import Employee


class Command(BaseCommand):
    help = 'Generate sample data for 20 stores based on StoreForm fields'

    def handle(self, *args, **options):
        # Predefined lists for realistic data
        cities = ['Mbabane', 'Manzini', 'Lobamba', 'Siteki', 'Piggs Peak', 'Nhlangano', 'Mhlume', 'Big Bend']
        regions = ['Hhohho', 'Manzini', 'Lubombo', 'Shiselweni']
        street_names = ['Main Street', 'Church Avenue', 'Independence Road', 'King Street', 'Queen Street', 'Market Road']
        store_names = ['Downtown Store', 'Mall Branch', 'Corner Shop', 'Super Center', 'Express Outlet', 'Flagship Location', 'Warehouse Depot', 'Franchise Unit', 'Pop-up Shop', 'Regional Hub']
        descriptions = ['A modern retail store offering a wide range of products.', 'Specialized outlet for discounted items.', 'Full-service flagship location.', 'Convenient neighborhood store.', 'Large warehouse with bulk options.']
        secondary_contacts = ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'David Brown', 'Lisa Davis', 'Tom Miller', 'Anna Garcia', None]

        # Get all employees for manager assignment (optional)
        employees = list(Employee.objects.all())
        manager_choices = employees + [None] * 5  # Mostly None, some employees

        stores_created = 0
        for i in range(1, 21):
            # Generate required fields
            name = f"Swati {random.choice(store_names)} {i}"
            address = f"{random.randint(1, 999)} {random.choice(street_names)}"
            city = random.choice(cities)
            region = random.choice(regions)
            postal_code = f"{region[0].upper()}{random.randint(100, 999)}" if random.choice([True, False]) else None
            phone = f"{random.randint(70000000, 79999999)}"  # 8 digits for local part
            opening_date = date.today() - timedelta(days=random.randint(365, 3650))  # 1-10 years ago

            # Optional fields
            manager = random.choice(manager_choices) if manager_choices else None
            email = f"store{i}@example.com" if random.choice([True, False]) else None
            website_url = f"https://store{i}.com" if random.choice([True, False]) else None
            fax_number = f"{random.randint(70000000, 79999999)}" if random.choice([True, False]) else None
            secondary_contact = random.choice(secondary_contacts)
            store_type = random.choice([choice[0] for choice in STORE_TYPE_CHOICES])
            store_size = round(random.uniform(100, 1000), 2) if random.choice([True, False]) else None
            description = random.choice(descriptions) if random.choice([True, False]) else None
            status = random.choices([choice[0] for choice in STORE_STATUS_CHOICES], weights=[80, 5, 10, 5])[0]  # Mostly active
            opening_time = time(hour=random.randint(8, 10), minute=0) if random.choice([True, False]) else None
            closing_time = time(hour=random.randint(17, 20), minute=0) if random.choice([True, False]) else None
            latitude = round(random.uniform(-27.0, -25.5), 6) if random.choice([True, False]) else None  # Eswatini range
            longitude = round(random.uniform(30.5, 32.0), 6) if random.choice([True, False]) else None

            # Create the store
            store = Store.objects.create(
                name=name,
                address=address,
                city=city,
                region=region,
                postal_code=postal_code,
                phone=phone,
                opening_date=opening_date,
                manager=manager,
                email=email,
                website_url=website_url,
                fax_number=fax_number,
                secondary_contact=secondary_contact,
                store_type=store_type,
                store_size=store_size,
                description=description,
                status=status,
                opening_time=opening_time,
                closing_time=closing_time,
                latitude=latitude,
                longitude=longitude,
            )
            stores_created += 1
            self.stdout.write(self.style.SUCCESS(f'Created store: {store.name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {stores_created} sample stores.'))
