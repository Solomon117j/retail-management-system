# sales/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
# from inventory.models import Product

class Customer(models.Model):
    MEMBERSHIP_CHOICES = [
        ('basic', 'Basic'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    CONTACT_METHOD_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('mail', 'Mail'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    REFERRAL_SOURCE_CHOICES = [
        ('word_of_mouth', 'Word of Mouth'),
        ('social_media', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('website', 'Website'),
        ('friend_family', 'Friend/Family'),
        ('search_engine', 'Search Engine'),
        ('other', 'Other'),
    ]

    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('german', 'German'),
        ('chinese', 'Chinese'),
        ('japanese', 'Japanese'),
        ('other', 'Other'),
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
    middle_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Middle Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name="Country")
    state = models.CharField(max_length=50, blank=True, null=True, verbose_name="State/Province")
    join_date = models.DateField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Date of Birth")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    social_media = models.CharField(max_length=100, blank=True, null=True, verbose_name="Social Media Handle")
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default='email',
        verbose_name="Preferred Contact Method"
    )
    occupation = models.CharField(max_length=100, blank=True, null=True, verbose_name="Occupation")
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name="Marital Status"
    )
    number_of_dependents = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name="Number of Dependents"
    )
    referral_source = models.CharField(
        max_length=20,
        choices=REFERRAL_SOURCE_CHOICES,
        blank=True,
        null=True,
        verbose_name="How did you hear about us?"
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Emergency Contact Name")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Emergency Contact Phone")
    language_preference = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='english',
        verbose_name="Preferred Language"
    )
    data_processing_consent = models.BooleanField(default=False, verbose_name="Data Processing Consent")
    email_notifications = models.BooleanField(default=True, verbose_name="Email Notifications")
    sms_notifications = models.BooleanField(default=False, verbose_name="SMS Notifications")
    push_notifications = models.BooleanField(default=False, verbose_name="Push Notifications")
    marketing_opt_in = models.BooleanField(default=False, verbose_name="Marketing Opt-in")
    notes = models.TextField(blank=True, null=True, verbose_name="Customer Notes")
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

    SALES_CHANNEL_CHOICES = [
        ('in_store', 'In-Store'),
        ('online', 'Online'),
        ('phone', 'Phone'),
        ('marketplace', 'Marketplace'),
    ]

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    store = models.ForeignKey(
        'store_management.Store',
        on_delete=models.PROTECT,
        related_name='sales'
    )
    employee = models.ForeignKey(
        'accounts.Employee',
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
    sales_channel = models.CharField(
        max_length=20,
        choices=SALES_CHANNEL_CHOICES,
        default='in_store',
        verbose_name="Sales Channel"
    )
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='completed',
        verbose_name="Order Status"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Sale Notes")
    delivery_address = models.TextField(blank=True, null=True, verbose_name="Delivery Address")
    invoice_number = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Invoice Number")
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
        'accounts.Employee',
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