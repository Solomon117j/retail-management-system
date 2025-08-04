from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

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
        'inventory.Product',  # Reference to Product in inventory app
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
        'human_resources.Employee',  # Reference to Employee model
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