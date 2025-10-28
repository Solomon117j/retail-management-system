from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'

    def __str__(self):
        return self.name


class Product(models.Model):
    CRITICALITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="SKU")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=10, verbose_name="Reorder Level")
    safety_stock = models.IntegerField(default=0, verbose_name="Safety Stock Level", help_text="Minimum stock to maintain as buffer")
    sales_velocity = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name="Sales Velocity", help_text="Average units sold per day")
    demand_variability = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Demand Variability", help_text="Coefficient of variation for demand (0-1)")
    criticality = models.CharField(max_length=10, choices=CRITICALITY_CHOICES, default='MEDIUM', verbose_name="Criticality", help_text="Importance level for inventory management")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Barcode")
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Weight (kg)")
    length = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Length (cm)")
    width = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Width (cm)")
    height = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Height (cm)")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Product Image")
    default_supplier = models.ForeignKey('procurement.Supplier', on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'

    def __str__(self):
        return self.name


class InventoryRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_records')
    store = models.ForeignKey('store_management.Store', on_delete=models.CASCADE, related_name='inventory_records')
    quantity = models.IntegerField(default=0)
    location = models.CharField(max_length=200, blank=True, null=True)
    batch_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Batch Number")
    expiration_date = models.DateField(blank=True, null=True, verbose_name="Expiration Date")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Cost Price")
    supplier = models.ForeignKey('procurement.Supplier', on_delete=models.SET_NULL, blank=True, null=True, related_name='inventory_records')
    last_updated_by = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, blank=True, null=True, related_name='updated_inventory_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'
        unique_together = ['product', 'store']

    def __str__(self):
        return f"{self.product.name} - {self.store.name} - {self.quantity}"

    @property
    def is_expired(self):
        if self.expiration_date:
            return self.expiration_date < timezone.now().date()
        return False

    @property
    def expiring_soon(self):
        if self.expiration_date:
            today = timezone.now().date()
            config = ExpirationConfig.get_default_config()
            critical_threshold = today + timezone.timedelta(days=config.get_threshold_days('critical'))
            return today <= self.expiration_date <= critical_threshold
        return False


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
    ]

    REASON_CHOICES = [
        ('SALE', 'Sale'),
        ('PURCHASE', 'Purchase'),
        ('RETURN', 'Return'),
        ('DAMAGE', 'Damage'),
        ('THEFT', 'Theft'),
        ('ADJUSTMENT', 'Adjustment'),
        ('AUTO_REORDER', 'Auto Reorder'),
        ('TRANSFER', 'Transfer'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    store = models.ForeignKey('store_management.Store', on_delete=models.CASCADE, related_name='stock_movements')
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE_CHOICES)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="Reference (e.g., PO Number)")
    created_by = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'inventory'

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"


class InventoryAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('EXPIRING_SOON', 'Expiring Soon'),
        ('OVERSTOCK', 'Overstock'),
        ('AUTO_REORDER', 'Auto Reorder Triggered'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]

    inventory_record = models.ForeignKey(InventoryRecord, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    message = models.TextField()
    threshold_value = models.IntegerField(blank=True, null=True, help_text="The threshold that triggered this alert")
    current_value = models.IntegerField(blank=True, null=True, help_text="Current inventory level")
    auto_resolved = models.BooleanField(default=False, help_text="Whether this alert was resolved automatically")
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.inventory_record.product.name} ({self.priority})"

    def resolve(self, user=None):
        """Mark the alert as resolved"""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        if user:
            self.resolved_by = user
        self.save()


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('DELIVERED', 'Delivered'),
    ]

    alert = models.ForeignKey(InventoryAlert, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    recipient = models.CharField(max_length=100, help_text="Email address, phone number, or user ID")
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} to {self.recipient} - {self.status}"


class ExpirationConfig(models.Model):
    """
    Configuration for expiration date tracking and alerts
    """
    name = models.CharField(max_length=100, unique=True, help_text="Configuration name (e.g., 'Default', 'Perishable Goods')")
    alert_thresholds = models.JSONField(
        default=dict,
        help_text="Alert thresholds in days (e.g., {'critical': 7, 'warning': 14, 'info': 30})"
    )
    auto_prevent_sales = models.BooleanField(
        default=True,
        help_text="Automatically prevent sales of expired items"
    )
    notification_recipients = models.JSONField(
        default=list,
        help_text="List of recipient groups (e.g., ['Management', 'Inventory', 'Procurement'])"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'
        verbose_name = 'Expiration Configuration'
        verbose_name_plural = 'Expiration Configurations'

    def __str__(self):
        return self.name

    def get_threshold_days(self, level='warning'):
        """Get threshold days for a specific alert level"""
        return self.alert_thresholds.get(level, 30)

    @classmethod
    def get_default_config(cls):
        """Get the default expiration configuration"""
        config, created = cls.objects.get_or_create(
            name='Default',
            defaults={
                'alert_thresholds': {
                    'critical': 7,
                    'warning': 14,
                    'info': 30
                },
                'auto_prevent_sales': True,
                'notification_recipients': ['Management', 'Inventory', 'Procurement']
            }
        )
        return config


class ReplenishmentConfig(models.Model):
    """
    System-wide configuration for automated replenishment workflows
    """
    name = models.CharField(max_length=100, unique=True, help_text="Configuration name (e.g., 'Default', 'High-Value Items')")
    auto_replenishment_enabled = models.BooleanField(default=True, help_text="Enable automatic replenishment processing")
    batch_processing_enabled = models.BooleanField(default=True, help_text="Enable bulk procurement batching")
    auto_approval_enabled = models.BooleanField(default=False, help_text="Enable automatic approval of purchase orders")
    max_auto_approval_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00, help_text="Maximum PO amount for auto-approval")
    safety_stock_multiplier = models.DecimalField(max_digits=3, decimal_places=1, default=1.5, help_text="Multiplier for safety stock calculation")
    lead_time_buffer_days = models.IntegerField(default=2, help_text="Extra days to add to lead time for safety")
    min_order_frequency_days = models.IntegerField(default=7, help_text="Minimum days between automatic orders for same product")
    notification_enabled = models.BooleanField(default=True, help_text="Enable replenishment notifications")
    notification_recipients = models.JSONField(default=list, help_text="List of recipient groups for notifications")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'
        verbose_name = 'Replenishment Configuration'
        verbose_name_plural = 'Replenishment Configurations'

    def __str__(self):
        return self.name

    @classmethod
    def get_default_config(cls):
        """Get the default replenishment configuration"""
        config, created = cls.objects.get_or_create(
            name='Default',
            defaults={
                'auto_replenishment_enabled': True,
                'batch_processing_enabled': True,
                'auto_approval_enabled': False,
                'max_auto_approval_amount': 1000.00,
                'safety_stock_multiplier': 1.5,
                'lead_time_buffer_days': 2,
                'min_order_frequency_days': 7,
                'notification_enabled': True,
                'notification_recipients': ['Management', 'Procurement']
            }
        )
        return config


class ReplenishmentBatch(models.Model):
    """
    Tracks bulk procurement batches for optimized ordering
    """
    BATCH_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    batch_id = models.CharField(max_length=50, unique=True, help_text="Unique batch identifier")
    supplier = models.ForeignKey('procurement.Supplier', on_delete=models.CASCADE, related_name='replenishment_batches')
    store = models.ForeignKey('store_management.Store', on_delete=models.CASCADE, related_name='replenishment_batches')
    status = models.CharField(max_length=20, choices=BATCH_STATUS_CHOICES, default='PENDING')
    total_items = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    purchase_order = models.OneToOneField('procurement.PurchaseOrder', on_delete=models.SET_NULL, blank=True, null=True, related_name='replenishment_batch')
    processing_started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch {self.batch_id} - {self.supplier.name} ({self.status})"

    def add_item(self, product, quantity, unit_price):
        """Add an item to the replenishment batch"""
        batch_item, created = ReplenishmentBatchItem.objects.get_or_create(
            batch=self,
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': unit_price,
                'line_total': quantity * unit_price
            }
        )
        if not created:
            batch_item.quantity += quantity
            batch_item.line_total = batch_item.quantity * batch_item.unit_price
            batch_item.save()

        self.total_items += 1
        self.total_value += quantity * unit_price
        self.save()

    def create_purchase_order(self):
        """Create a purchase order from this batch"""
        from procurement.models import PurchaseOrder, PurchaseOrderItem

        with transaction.atomic():
            # Create the purchase order
            po = PurchaseOrder.objects.create(
                supplier=self.supplier,
                store=self.store,
                status='draft',
                created_by=self.created_by
            )

            # Add items from batch
            for batch_item in self.replenishment_items.all():
                PurchaseOrderItem.objects.create(
                    order=po,
                    product=batch_item.product,
                    quantity=batch_item.quantity,
                    unit_price=batch_item.unit_price
                )

            # Link PO to batch
            self.purchase_order = po
            self.status = 'COMPLETED'
            self.completed_at = timezone.now()
            self.save()

            return po


class ReplenishmentBatchItem(models.Model):
    """
    Individual items within a replenishment batch
    """
    batch = models.ForeignKey(ReplenishmentBatch, on_delete=models.CASCADE, related_name='replenishment_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'inventory'
        unique_together = ['batch', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class StockTransfer(models.Model):
    """
    Model for tracking stock transfers between stores
    """
    TRANSFER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('IN_TRANSIT', 'In Transit'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    transfer_id = models.CharField(max_length=50, unique=True, help_text="Unique transfer identifier")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_transfers')
    from_store = models.ForeignKey('store_management.Store', on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_store = models.ForeignKey('store_management.Store', on_delete=models.CASCADE, related_name='incoming_transfers')
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=TRANSFER_STATUS_CHOICES, default='PENDING')
    requested_by = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, blank=True, null=True, related_name='requested_transfers')
    approved_by = models.ForeignKey('human_resources.Employee', on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_transfers')
    approved_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    received_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'inventory'
        ordering = ['-created_at']
        unique_together = ['transfer_id']

    def __str__(self):
        return f"Transfer {self.transfer_id}: {self.product.name} ({self.quantity}) from {self.from_store.name} to {self.to_store.name}"

    def approve(self, user):
        """Approve the transfer"""
        if self.status == 'PENDING':
            self.status = 'APPROVED'
            self.approved_by = user
            self.approved_at = timezone.now()
            self.save()

    def ship(self):
        """Mark transfer as shipped"""
        if self.status == 'APPROVED':
            self.status = 'IN_TRANSIT'
            self.shipped_at = timezone.now()
            self.save()

    def receive(self):
        """Mark transfer as received and update inventory"""
        if self.status == 'IN_TRANSIT':
            with transaction.atomic():
                # Reduce stock from source store
                from_inventory, created = InventoryRecord.objects.get_or_create(
                    product=self.product,
                    store=self.from_store,
                    defaults={'quantity': 0}
                )
                from_inventory.quantity -= self.quantity
                from_inventory.save()

                # Increase stock at destination store
                to_inventory, created = InventoryRecord.objects.get_or_create(
                    product=self.product,
                    store=self.to_store,
                    defaults={'quantity': 0}
                )
                to_inventory.quantity += self.quantity
                to_inventory.save()

                # Create stock movements
                StockMovement.objects.create(
                    product=self.product,
                    store=self.from_store,
                    quantity=-self.quantity,
                    movement_type='OUT',
                    reason='TRANSFER',
                    reference=f"Transfer-{self.transfer_id}",
                    created_by=self.requested_by
                )

                StockMovement.objects.create(
                    product=self.product,
                    store=self.to_store,
                    quantity=self.quantity,
                    movement_type='IN',
                    reason='TRANSFER',
                    reference=f"Transfer-{self.transfer_id}",
                    created_by=self.requested_by
                )

                self.status = 'RECEIVED'
                self.received_at = timezone.now()
                self.save()
