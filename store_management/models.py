from django.db import models


class Store(models.Model):
    """Stores model."""
    id = models.AutoField(primary_key=True, db_column='store_id')
    
    store_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20)
    opening_date = models.DateField()
    # Use string reference instead of direct import
    manager = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_stores')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_management_store'

    def __str__(self):
        return self.store_name

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='departments')
   
    manager = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

       
    @property
    def can_be_deleted(self):
        """
        Check if the department can be safely deleted.
        Add any business logic constraints here.
        """
        # Example: Can be deleted if no employees are assigned
        # return self.employee_set.count() == 0
        
        # For now, always allow deletion
        return True

    class Meta:
        ordering = ['department_name']
        db_table = 'store_management_department'
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'department_name'],
                name='unique_department_per_store'
            )
        ]

    def __str__(self):
        return self.department_name