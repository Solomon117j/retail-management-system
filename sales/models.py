# sales/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Customer(models.Model):
    MEMBERSHIP_CHOICES = [
        ('basic', 'Basic'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    customer_account = models.OneToOneField(
        'e_commerce.CustomerAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_customer',
        help_text="Link to the customer account from the customer portal"
    )
    
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    membership_level = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='basic'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('digital_wallet', 'Digital Wallet'),
        ('store_credit', 'Store Credit'),
    ]
    
    store = models.ForeignKey(
        'store_management.Store',
        on_delete=models.PROTECT,
        related_name='sales'
    )
    employee = models.ForeignKey(
        'human_resources.Employee',
        on_delete=models.PROTECT,
        related_name='sales'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='purchases'
    )
    sale_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"Sale #{self.id} - {self.sale_date.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Calculate total if not set and items exist
        if not self.total_amount and self.id:
            self.total_amount = sum(
                item.quantity * item.unit_price * (1 - item.discount_percentage / 100)
                for item in self.items.all()
            )
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
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
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sale Item"
        verbose_name_plural = "Sale Items"
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price * (1 - self.discount_percentage / 100)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update parent sale total
        self.sale.save()

class Return(models.Model):
    REFUND_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('store_credit', 'Store Credit'),
    ]
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name='returns'
    )
    return_date = models.DateTimeField(default=timezone.now)
    reason = models.CharField(max_length=200, blank=True, null=True)
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    refund_method = models.CharField(
        max_length=20,
        choices=REFUND_METHOD_CHOICES
    )
    employee = models.ForeignKey(
        'human_resources.Employee',
        on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Return"
        verbose_name_plural = "Returns"
        ordering = ['-return_date']
    
    def __str__(self):
        return f"Return #{self.id} for Sale #{self.sale_id}"

class LoyaltyTransaction(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='loyalty_transactions'
    )
    sale = models.ForeignKey(
        Sale,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='loyalty_transactions'
    )
    points_earned = models.IntegerField(default=0)
    points_redeemed = models.IntegerField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Loyalty Transaction"
        verbose_name_plural = "Loyalty Transactions"
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"Loyalty TX #{self.id} - {self.customer}"
    
    def save(self, *args, **kwargs):
        # Update customer loyalty points
        if not self.pk:  # Only on creation
            self.customer.loyalty_points += (self.points_earned - self.points_redeemed)
            self.customer.save()
        super().save(*args, **kwargs)

class SalesTransaction(models.Model):
    # Add your fields here
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    # Add other fields as needed

    def __str__(self):
        return f"Transaction {self.id} - {self.date}"