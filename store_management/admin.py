from django.contrib import admin

# Register your models here.

from .models import Store, Department
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'region', 'postal_code', 'phone', 'opening_date')
    search_fields = ('name', 'city', 'region')
    list_filter = ('region',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'description')
    search_fields = ('department_name',)