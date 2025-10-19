import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings  # Import settings to access AUTH_USER_MODEL
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
# from inventory.models import Product

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

    # Optimized UX Enhancement Fields
    preferred_language = models.CharField(
        max_length=10,
        default='en',
        choices=[('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('si', 'siSwati')],
        verbose_name="Preferred Language"
    )
    marketing_opt_in = models.BooleanField(default=False, verbose_name="Marketing Communications")
    sms_notifications = models.BooleanField(default=False, verbose_name="SMS Notifications")
    push_notifications = models.BooleanField(default=True, verbose_name="Push Notifications")

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

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    customer = models.ForeignKey(
        CustomerAccount,
        on_delete=models.PROTECT,
        related_name='online_orders',
        null=True,
        blank=True  # Allow guest checkout
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
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    payment_date = models.DateTimeField(blank=True, null=True)

    # Guest checkout support
    guest_email = models.EmailField(blank=True, null=True, verbose_name="Guest Email")
    guest_first_name = models.CharField(max_length=50, blank=True, null=True)
    guest_last_name = models.CharField(max_length=50, blank=True, null=True)
    guest_phone = models.CharField(max_length=20, blank=True, null=True)

    # Enhanced guest information
    guest_company = models.CharField(max_length=100, blank=True, null=True, verbose_name="Company Name")
    guest_birth_date = models.DateField(blank=True, null=True, verbose_name="Date of Birth")
    guest_preferred_language = models.CharField(
        max_length=10,
        default='en',
        choices=[('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('si', 'siSwati')],
        verbose_name="Preferred Language"
    )

    # Billing address (separate from shipping)
    billing_address = models.TextField(blank=True, null=True, verbose_name="Billing Address")
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_state = models.CharField(max_length=100, blank=True, null=True)
    billing_postal_code = models.CharField(max_length=20, blank=True, null=True)
    billing_country = models.CharField(max_length=100, blank=True, null=True)

    # Marketing and communication preferences
    guest_marketing_opt_in = models.BooleanField(default=False, verbose_name="Marketing Communications")
    guest_sms_notifications = models.BooleanField(default=False, verbose_name="SMS Notifications")
    guest_push_notifications = models.BooleanField(default=True, verbose_name="Push Notifications")

    # Order customization
    order_notes = models.TextField(blank=True, null=True, verbose_name="Order Notes/Special Instructions")
    gift_wrapping = models.BooleanField(default=False, verbose_name="Gift Wrapping")
    gift_message = models.TextField(blank=True, null=True, verbose_name="Gift Message")
    loyalty_program_signup = models.BooleanField(default=False, verbose_name="Join Loyalty Program")
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
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    product_name = models.CharField(max_length=100, blank=True)  # Keep for display purposes
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        default=0.01
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        # Removed unique constraint on product as field is removed
    
    def __str__(self):
        product_display = self.product.name if self.product else self.product_name
        return f"{self.quantity} x {product_display}"
    
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
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def tax_amount(self):
        return Decimal(self.subtotal) * Decimal('0.15')  # 15% tax

    @property
    def total_price(self):
        return self.subtotal + self.tax_amount

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
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product_name = models.CharField(max_length=100, blank=True)  # Keep for display purposes
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        default=0.01
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        # Removed unique constraint on product as field is removed

    def __str__(self):
        product_display = self.product.name if self.product else self.product_name
        return f"{self.quantity} x {product_display}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

class SavedPaymentMethod(models.Model):
    """
    Saved payment methods for faster checkout
    """
    PAYMENT_TYPE_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('digital_wallet', 'Digital Wallet'),
    ]

    customer = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='saved_payment_methods'
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES
    )
    card_last_four = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name="Last 4 Digits"
    )
    card_brand = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Card Brand"
    )
    expiry_month = models.PositiveIntegerField(blank=True, null=True)
    expiry_year = models.PositiveIntegerField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Saved Payment Method"
        verbose_name_plural = "Saved Payment Methods"
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'is_default'],
                name='unique_default_payment',
                condition=models.Q(is_default=True)
            )
        ]

    def __str__(self):
        if self.card_last_four:
            return f"{self.get_payment_type_display()} ****{self.card_last_four}"
        return f"{self.get_payment_type_display()}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Remove default flag from other payment methods
            SavedPaymentMethod.objects.filter(
                customer=self.customer,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
