from django.db import models

# Create your models here.
# from apps.human_resources.models import Employee

class Store(models.Model):
    """Stores model."""
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20)
    opening_date = models.DateField()
    # manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_stores')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_management_store'

    def __str__(self):
        return self.store_name

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='departments')
    # manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Ensure that the department name is unique within a store
    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            
    class Meta:
        db_table = 'store_management_department'

    def __str__(self):
        return self.department_name
    

    # models.py
class Department(models.Model):
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )