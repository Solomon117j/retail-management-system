# ecommerce/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class OnlineOrder(models.Model):
    SHIPPING_METHOD_CHOICES = [
        ('standard', 'Standard Shipping'),
        ('express', 'Express Shipping'),
        ('store_pickup', 'Store Pickup'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('digital_wallet', 'Digital Wallet'),
    ]
    
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.PROTECT,
        related_name='online_orders'
    )
    order_date = models.DateTimeField(default=timezone.now)
    shipping_address = models.CharField(max_length=200)
    shipping_method = models.CharField(
        max_length=20,
        choices=SHIPPING_METHOD_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    store_pickup = models.ForeignKey(
        'store_management.Store',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='pickup_orders'
    )
    tracking_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Online Order"
        verbose_name_plural = "Online Orders"
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Online Order #{self.id} - {self.get_status_display()}"
    
    def clean(self):
        # Validate that store_pickup is set for store_pickup shipping method
        if self.shipping_method == 'store_pickup' and not self.store_pickup:
            raise ValidationError({
                'store_pickup': 'Store pickup location is required for store pickup shipping method.'
            })
        
        # Validate that tracking number is set for shipped orders
        if self.status in ['shipped', 'delivered'] and not self.tracking_number:
            raise ValidationError({
                'tracking_number': 'Tracking number is required for shipped orders.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-calculate total if not set and items exist
        if not self.total_amount and self.id:
            self.total_amount = sum(
                item.quantity * item.unit_price 
                for item in self.items.all()
            )
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(
        OnlineOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_order_product'
            )
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update parent order total
        self.order.save()