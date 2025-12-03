from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Client, Domain


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'created_on', 'paid_until', 'on_trial', 'is_active')
    list_filter = ('is_active', 'on_trial', 'created_on')
    search_fields = ('name', 'description')
    ordering = ('-created_on',)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')
