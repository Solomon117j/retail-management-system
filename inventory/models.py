from django.db import models
from django.contrib.auth import get_user_model

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
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="SKU")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=10, verbose_name="Reorder Level")
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
