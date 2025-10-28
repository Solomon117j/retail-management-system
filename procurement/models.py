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

    # Dropshipping Integration Fields
    is_dropshipping_supplier = models.BooleanField(
        default=False,
        verbose_name="Dropshipping Supplier",
        help_text="Check if this supplier supports dropshipping"
    )
    platform_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Platform Type",
        help_text="e.g., DSers, AliExpress, Oberlo",
        choices=[
            ('dsers', 'DSers'),
            ('aliexpress', 'AliExpress'),
            ('oberlo', 'Oberlo'),
            ('other', 'Other'),
        ]
    )
    platform_supplier_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Platform Supplier ID",
        help_text="Supplier ID on the dropshipping platform"
    )
    auto_sync_inventory = models.BooleanField(
        default=False,
        verbose_name="Auto Sync Inventory",
        help_text="Automatically sync inventory levels from platform"
    )
    auto_fulfill_orders = models.BooleanField(
        default=False,
        verbose_name="Auto Fulfill Orders",
        help_text="Automatically place orders on platform when sales occur"
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
    auto_approval_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Auto Approval Threshold",
        help_text="Maximum order value for automatic approval"
    )
    preferred_supplier = models.BooleanField(
        default=False,
        verbose_name="Preferred Supplier",
        help_text="This is the preferred supplier for this product"
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
        ('auto_approved', 'Auto Approved'),
        ('shipped', 'Shipped'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_TYPE_CHOICES = [
        ('supplier_order', 'Order from Supplier'),
        ('warehouse_transfer', 'Transfer from Warehouse'),
    ]

    order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPE_CHOICES,
        default='supplier_order',
        verbose_name="Order Type",
        help_text="Type of order: from supplier or warehouse transfer"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        blank=True,
        null=True
    )
    store = models.ForeignKey(
        'store_management.Store',  # Reference to Store model
        on_delete=models.PROTECT,
        verbose_name="Ordering Store"
    )
    destination_warehouse = models.ForeignKey(
        'store_management.Store',
        on_delete=models.PROTECT,
        related_name='received_transfers',
        blank=True,
        null=True,
        verbose_name="Destination Warehouse",
        help_text="Warehouse receiving the transfer (for warehouse transfers only)"
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
    replenishment_status = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual Order'),
            ('auto_triggered', 'Auto Triggered'),
            ('predictive', 'Predictive Reorder'),
            ('bulk_batch', 'Bulk Batch Order'),
        ],
        default='manual',
        verbose_name="Replenishment Status",
        help_text="How this order was created"
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_purchase_orders'
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


# DSers Integration Models
class DSersProduct(models.Model):
    """Model for DSers products imported into the system"""
    dsers_product_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="DSers Product ID"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='dsers_products'
    )
    product = models.OneToOneField(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='dsers_product'
    )
    dsers_data = models.JSONField(
        verbose_name="DSers Product Data",
        help_text="Raw JSON data from DSers API"
    )
    last_synced = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Synced"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this product is active for dropshipping"
    )

    def __str__(self):
        return f"DSers Product {self.dsers_product_id} - {self.product.name}"

    class Meta:
        verbose_name = "DSers Product"
        verbose_name_plural = "DSers Products"


class DSersOrder(models.Model):
    """Model for tracking DSers orders"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    dsers_order_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="DSers Order ID"
    )
    sales_order = models.ForeignKey(
        'e_commerce.OnlineOrder',
        on_delete=models.CASCADE,
        related_name='dsers_orders'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='dsers_orders'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name="Order Status"
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tracking Number"
    )
    shipping_carrier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Shipping Carrier"
    )
    dsers_data = models.JSONField(
        verbose_name="DSers Order Data",
        help_text="Raw JSON data from DSers API"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    def __str__(self):
        return f"DSers Order {self.dsers_order_id} - {self.status}"

    class Meta:
        verbose_name = "DSers Order"
        verbose_name_plural = "DSers Orders"
