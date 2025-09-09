from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.db.models import F


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Category Name")
    description = models.CharField(max_length=200, blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Parent Category"
    )

    # Ownership and access control fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_categories'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_categories'
    )
    department = models.ForeignKey(
        'store_management.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categories'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=50, verbose_name="Brand Name")
    description = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=100, blank=True, null=True)

    # Strong Identity Enhancement Fields
    brand_voice = models.TextField(
        blank=True,
        null=True,
        verbose_name="Brand Voice & Personality",
        help_text="Describe the brand's personality, tone, and communication style"
    )
    aesthetic_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Aesthetic Guidelines",
        help_text="Visual style, color preferences, design principles"
    )
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        verbose_name="Primary Color (Hex)",
        help_text="e.g., #FF5733"
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        verbose_name="Secondary Color (Hex)",
        help_text="e.g., #33FF57"
    )
    brand_story = models.TextField(
        blank=True,
        null=True,
        verbose_name="Brand Story",
        help_text="The narrative and values that define the brand"
    )
    logo = models.ImageField(
        upload_to='brand_logos/',
        blank=True,
        null=True,
        verbose_name="Brand Logo"
    )
    brand_assets = models.FileField(
        upload_to='brand_assets/',
        blank=True,
        null=True,
        verbose_name="Brand Assets (ZIP)",
        help_text="Upload brand guidelines, fonts, or other assets"
    )

    # Ownership and access control fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_brands'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_brands'
    )
    department = models.ForeignKey(
        'store_management.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brands'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Product Name")
    description = models.CharField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Unit Price"
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    dimensions = models.CharField(max_length=50, blank=True, null=True)

    # New fields for e-commerce visibility and imagery
    available_online = models.BooleanField(default=False, db_index=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    is_perishable = models.BooleanField(default=False)
    barcode = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    # Ownership and access control fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_products'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_products'
    )
    department = models.ForeignKey(
        'store_management.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def profit_margin(self):
        """Calculate profit margin as a percentage"""
        if self.cost_price and self.cost_price > 0:
            profit = self.unit_price - self.cost_price
            return round((profit / self.cost_price) * 100, 2)
        return None
    
    @property
    def profit_amount(self):
        """Calculate profit amount"""
        if self.cost_price:
            return self.unit_price - self.cost_price
        return None


class StoreInventory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_records'
    )
    store = models.ForeignKey(
        'store_management.Store',  # Reference to Store model in another app
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    last_restock_date = models.DateField(blank=True, null=True)
    aisle_location = models.CharField(max_length=20, blank=True, null=True)

    # Ownership and access control fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_inventory_records'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_inventory_records'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'store'],
                name='unique_product_store'
            )
        ]
        verbose_name_plural = "Store Inventory"

    def __str__(self):
        return f"{self.product.name} at {self.store.store_name}"


class StockMovement(models.Model):
    """Atomic stock movement record and applier.
    - IN, OUT, TRANSFER_IN/OUT use positive quantities.
    - ADJUST uses signed quantity (delta applied to current stock).
    """
    MOVEMENT_IN = 'IN'
    MOVEMENT_OUT = 'OUT'
    MOVEMENT_ADJUST = 'ADJUST'
    MOVEMENT_TRANSFER_IN = 'TRANSFER_IN'
    MOVEMENT_TRANSFER_OUT = 'TRANSFER_OUT'

    MOVEMENT_CHOICES = [
        (MOVEMENT_IN, 'Inbound'),
        (MOVEMENT_OUT, 'Outbound'),
        (MOVEMENT_ADJUST, 'Adjustment'),
        (MOVEMENT_TRANSFER_IN, 'Transfer In'),
        (MOVEMENT_TRANSFER_OUT, 'Transfer Out'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    store = models.ForeignKey('store_management.Store', on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.IntegerField()  # positive for IN/OUT/TRANSFER; signed for ADJUST
    reference = models.CharField(max_length=100, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type} {self.quantity} of {self.product} at {self.store}"

    def apply(self):
        """Apply the movement to StoreInventory atomically."""
        with transaction.atomic():
            inv, _ = StoreInventory.objects.select_for_update().get_or_create(
                product=self.product, store=self.store, defaults={'quantity': 0}
            )
            if self.movement_type in [self.MOVEMENT_IN, self.MOVEMENT_TRANSFER_IN]:
                inv.quantity = F('quantity') + abs(self.quantity)
                inv.last_restock_date = timezone.now().date()
            elif self.movement_type in [self.MOVEMENT_OUT, self.MOVEMENT_TRANSFER_OUT]:
                inv.quantity = F('quantity') - abs(self.quantity)
            elif self.movement_type == self.MOVEMENT_ADJUST:
                # quantity may be signed
                inv.quantity = F('quantity') + self.quantity
                if self.quantity > 0:
                    inv.last_restock_date = timezone.now().date()
            inv.save(update_fields=['quantity', 'last_restock_date', 'updated_at'])
            # Refresh to resolve F() expressions
            inv.refresh_from_db(fields=['quantity'])
            return inv.quantity

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        super().save(*args, **kwargs)
        # Only apply on first creation to avoid double applications
        if is_create:
            self.apply()