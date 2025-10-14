from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
# from inventory.models import Product

# Create your models here.
# procurement/models.py


class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="Supplier Name")
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)

    # Scalability Enhancement Fields
    api_endpoint = models.URLField(
        blank=True,
        null=True,
        verbose_name="API Endpoint",
        help_text="Third-party API endpoint for integration"
    )
    api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="API Key"
    )
    on_time_delivery_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="On-Time Delivery Rate (%)"
    )
    quality_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        verbose_name="Quality Rating (1-5)"
    )
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    compliance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Compliance Score (%)"
    )
    tenant_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Tenant ID",
        help_text="For multi-tenant architecture"
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name="Website",
        help_text="Supplier's website URL"
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Tax ID",
        help_text="Supplier's tax identification number"
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Industry",
        help_text="Industry or sector the supplier operates in"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Additional notes about the supplier"
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SupplierProduct(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='supplier_products'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE
    )
    supply_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    lead_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Lead Time (days)"
    )
    minimum_order_quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'product'],
                name='unique_supplier_product'
            )
        ]

    def __str__(self):
        return f"{self.product.name} from {self.supplier.name}"

class PurchaseOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )
    store = models.ForeignKey(
        'store_management.Store',  # Reference to Store model
        on_delete=models.PROTECT
    )
    order_date = models.DateField(default=timezone.now)
    expected_delivery_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='draft'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.01)]
    )
    created_by = models.ForeignKey(
        'accounts.Employee',  # Reference to Employee model
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO-{self.id} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount if not set
        if not self.total_amount and self.id:
            self.total_amount = sum(
                item.quantity * item.unit_price 
                for item in self.items.all()
            )
        super().save(*args, **kwargs)

class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    received_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def save(self, *args, **kwargs):
        # Update parent order total when item changes
        super().save(*args, **kwargs)
        self.order.save()  # Recalculate total_amount
