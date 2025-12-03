from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    """
    Represents a tenant (client/store) in the multi-tenant system.
    Each client has their own schema and domain.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    paid_until = models.DateTimeField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """
    Represents a domain for a tenant.
    Each tenant can have multiple domains.
    """
    pass
