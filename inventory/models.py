from django.db import models
from django.utils import timezone

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
    is_perishable = models.BooleanField(default=False)
    barcode = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
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
        return f"{self.product.name} at {self.store.name}"