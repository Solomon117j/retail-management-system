import uuid
from django.db import models

# Store type choices
STORE_TYPE_CHOICES = [
    ('retail', 'Retail Store'),
    ('flagship', 'Flagship Store'),
    ('outlet', 'Outlet Store'),
    ('warehouse', 'Warehouse'),
    ('franchise', 'Franchise'),
    ('pop_up', 'Pop-up Store'),
]

# Store status choices
STORE_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('under_renovation', 'Under Renovation'),
    ('closed', 'Closed'),
]


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """Stores model."""

    store_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Store Number",
        help_text="Unique store identifier, auto-generated if left blank"
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20)
    opening_date = models.DateField()
    manager = models.ForeignKey(
        'human_resources.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_stores',
        verbose_name="Store Manager"
    )

    # Additional contact and web information
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    website_url = models.URLField(blank=True, null=True, verbose_name="Website URL")
    fax_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Fax Number")
    secondary_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="Secondary Contact Person")

    # Store characteristics
    store_type = models.CharField(
        max_length=20,
        choices=STORE_TYPE_CHOICES,
        default='retail',
        verbose_name="Store Type"
    )
    store_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Store Size (sq m)",
        help_text="Store size in square meters"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Store Description")
    status = models.CharField(
        max_length=20,
        choices=STORE_STATUS_CHOICES,
        default='active',
        verbose_name="Store Status"
    )

    # Operating hours
    opening_time = models.TimeField(blank=True, null=True, verbose_name="Opening Time")
    closing_time = models.TimeField(blank=True, null=True, verbose_name="Closing Time")

    # GPS coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Longitude"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_management_store'

    def save(self, *args, **kwargs):
        if not self.store_number:
            # Generate unique store number
            import random
            import string
            while True:
                store_number = ''.join(random.choices(string.digits, k=6))
                if not Store.objects.filter(store_number=store_number).exists():
                    self.store_number = store_number
                    break
        super().save(*args, **kwargs)

    def generate_barcode_image(self):
        """Generate barcode image for the store number."""
        from barcode import Code128
        from barcode.writer import ImageWriter
        from io import BytesIO

        # Create barcode
        barcode = Code128(self.store_number, writer=ImageWriter())

        # Generate barcode as image in memory
        buffer = BytesIO()
        barcode.write(buffer)
        buffer.seek(0)
        return buffer

    def __str__(self):
        return self.name

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='departments')
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