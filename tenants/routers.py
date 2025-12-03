from django_tenants.routers import TenantSyncRouter
from django_tenants.utils import get_public_schema_name
from django.db import connections


class CustomTenantSyncRouter(TenantSyncRouter):
    """
    Custom router that handles cases where schema_name is not set on the connection.
    This can happen during makemigrations when middleware is not loaded.
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Ensure shared_apps and tenant_apps are set, as they might not be during makemigrations
        if not hasattr(self, 'shared_apps'):
            from django.conf import settings
            self.shared_apps = getattr(settings, 'SHARED_APPS', [])
            self.tenant_apps = getattr(settings, 'TENANT_APPS', [])

        connection = connections[db]
        # Check if schema_name is available on the connection
        if hasattr(connection, 'schema_name'):
            # Use the original logic if schema_name is available
            return super().allow_migrate(db, app_label, model_name, **hints)
        else:
            # If schema_name is not available (e.g., during makemigrations),
            # assume we're working with the public schema for shared apps
            if app_label in self.shared_apps:
                return True
            else:
                # For tenant apps, we need to be more careful
                # During initial setup, allow migrations for tenant apps on public schema
                return True
