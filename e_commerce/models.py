import uuid
from django.db import models
from django.conf import settings  # Import settings to access AUTH_USER_MODEL
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class CustomerAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """
    Extended user profile model with customer-specific information
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Use swappable user model
        on_delete=models.CASCADE,
        null=True,  # Allow null during initial migration to avoid default prompt
        blank=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    class Meta:
        verbose_name = "Customer Account"
        verbose_name_plural = "Customer Accounts"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class OnlineOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """
    Model representing online orders placed by customers
    """
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
        CustomerAccount,
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
        validators=[MinValueValidator(0.01)],
        default=0.00
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Online Order"
        verbose_name_plural = "Online Orders"
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Online Order #{self.id} - {self.get_status_display()}"
    
    def clean(self):
        """Additional validation rules"""
        if self.shipping_method == 'store_pickup' and not self.store_pickup:
            raise ValidationError({
                'store_pickup': 'Store pickup location is required for store pickup shipping method.'
            })
        
        if self.status in ['shipped', 'delivered'] and not self.tracking_number:
            raise ValidationError({
                'tracking_number': 'Tracking number is required for shipped orders.'
            })
    
    def save(self, *args, **kwargs):
        """Recalculate total from items when saving"""
        if self.pk:
            self.total_amount = sum(item.total_price for item in self.items.all())
        super().save(*args, **kwargs)

    @property
    def item_count(self):
        return self.items.count()

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """
    Individual items within an online order
    """
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
    created_at = models.DateTimeField(auto_now_add=True)
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
        self.order.save()

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """
    Shopping cart for customers
    """
    customer = models.OneToOneField(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart for {self.customer}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """
    Individual items in the shopping cart
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_product'
            )
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.unit_price
