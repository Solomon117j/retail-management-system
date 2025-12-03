# TODO: Improve Allowed Domains as per Tenants

## Tasks
- [x] Create DynamicTenantList class in settings.py to dynamically include tenant domains
- [x] Update ALLOWED_HOSTS to use DynamicTenantList
- [x] Update CSRF_TRUSTED_ORIGINS to use DynamicTenantList
- [x] Test the configuration to ensure tenant domains are properly allowed
