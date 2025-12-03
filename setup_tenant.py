import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from tenants.models import Client, Domain

def create_tenants():
    """
    Create default and juice tenants for development.
    """
    # Create default tenant
    if not Client.objects.filter(schema_name='default').exists():
        # Delete any incorrectly created public tenant
        Client.objects.filter(schema_name='public').delete()

        default_tenant = Client.objects.create(
            schema_name='default',
            name='Default Tenant',
            description='Default tenant for development',
            paid_until=datetime.now() + timedelta(days=365),
            on_trial=True,
            is_active=True
        )
        print(f"Created tenant: {default_tenant.name} with schema: {default_tenant.schema_name}")

        # Create domains for localhost
        domains = ['127.0.0.1', 'localhost']
        for domain_name in domains:
            domain, created = Domain.objects.get_or_create(
                domain=domain_name,
                defaults={'tenant': default_tenant, 'is_primary': True}
            )
            if created:
                print(f"Created domain: {domain.domain} for tenant {default_tenant.name}")
            else:
                print(f"Domain {domain.domain} already exists")
    else:
        print("Default tenant already exists.")

    # Create juice tenant
    if not Client.objects.filter(schema_name='juice').exists():
        juice_tenant = Client.objects.create(
            schema_name='juice',
            name='Juice Tenant',
            description='Tenant for juice-related operations',
            paid_until=datetime.now() + timedelta(days=365),
            on_trial=True,
            is_active=True
        )
        print(f"Created tenant: {juice_tenant.name} with schema: {juice_tenant.schema_name}")

        # Create domain for juice tenant (example: juice.localhost)
        domain, created = Domain.objects.get_or_create(
            domain='juice.localhost',
            defaults={'tenant': juice_tenant, 'is_primary': True}
        )
        if created:
            print(f"Created domain: {domain.domain} for tenant {juice_tenant.name}")
        else:
            print(f"Domain {domain.domain} already exists")
    else:
        print("Juice tenant already exists.")

if __name__ == '__main__':
    create_tenants()
