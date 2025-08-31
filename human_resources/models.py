from django.contrib.auth.models import Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class Employee(AbstractUser):
    # Primary key (replaces default 'id' field)
    employee_id = models.AutoField(primary_key=True)
    
    # Personal info (override AbstractUser fields)
    first_name = models.CharField(_("first name"), max_length=50, blank=False)
    last_name = models.CharField(_("last name"), max_length=50, blank=False)
    email = models.EmailField(_("email address"), unique=True)  # Uncommented and made unique
    
    # Additional fields
    phone = models.CharField(_("phone number"), max_length=20, blank=True, null=True)
    hire_date = models.DateField(_("hire date"), blank=True, null=True)
    position = models.CharField(_("position"), max_length=50, blank=True)
    salary = models.DecimalField(
        _("salary"), 
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    
    # Relationships
    department = models.ForeignKey(
        'store_management.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("department")
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='username'
    )
    store = models.ForeignKey(
        'store_management.Store',
        on_delete=models.SET_NULL,
        null=True,       # Add this
        blank=True,      # Add this
        verbose_name='Assigned Store'
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("manager")
    )
    
    # Profile image
    profile_image = models.ImageField(
        _("profile image"),
        upload_to='employee_profiles/',
        blank=True,
        null=True,
        help_text=_("Upload a profile picture for this employee")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        Group,
        related_name="hr_employees",  # Unique name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="hr_employees",  # Unique name
        blank=True,
    )
    class Meta:        
        db_table = 'human_resources_employee'
        verbose_name = _("employee")
        verbose_name_plural = _("employees")
        ordering = ['last_name', 'first_name']
        permissions = [
            # StoreManagement Permissions
            ("view_store_dashboard", "Can view store management dashboard"),
            ("manage_store_settings", "Can modify store configuration and settings"),
            ("manage_departments", "Can create/edit/delete store departments"),
            
            # Inventory Permissions
            ("access_inventory", "Can access inventory management system"),
            ("view_inventory", "Can view inventory items and stock levels"),
            ("edit_inventory", "Can modify inventory items and quantities"),
            ("manage_inventory_categories", "Can organize inventory categories"),
            ("perform_inventory_audit", "Can conduct physical inventory counts"),
            
            # Sales Permissions
            ("process_sales", "Can process in-store sales transactions"),
            ("void_sales", "Can void/completely cancel sales transactions"),
            ("manage_sales_promotions", "Can configure sales promotions/discounts"),
            ("view_sales_reports", "Can access sales performance reports"),
            
            # Procurement Permissions
            ("create_purchase_orders", "Can generate new procurement orders"),
            ("approve_purchase_orders", "Can authorize procurement requests"),
            ("manage_suppliers", "Can maintain supplier/vendor records"),
            ("receive_stock", "Can process received shipments"),
            
            # HumanResources Permissions
            ("view_employee_directory", "Can access employee contact information"),
            ("manage_employee_records", "Can maintain HR records (excluding sensitive data)"),
            ("access_hr_reports", "Can view HR analytics and reports"),
            ("manage_recruitment", "Can handle hiring processes"),
            
            # ECommerce Permissions
            ("manage_online_listings", "Can maintain e-commerce product listings"),
            ("process_online_orders", "Can fulfill e-commerce purchases"),
            ("handle_customer_portals", "Can manage customer account portals"),
            ("view_web_analytics", "Can access e-commerce traffic/revenue reports"),
            
            # Reporting Permissions
            ("generate_financial_reports", "Can create financial statements"),
            ("export_data_reports", "Can export datasets for external analysis"),
            ("access_executive_dashboards", "Can view strategic business dashboards"),
            ("schedule_automated_reports", "Can configure report automation"),
            
            # Cross-Module Permissions
            ("override_inventory_checks", "Can bypass inventory validation rules"),
            ("access_audit_logs", "Can view system audit trails"),
            ("manage_api_integrations", "Can configure system integrations")
        ]
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Ensure username is handled properly if needed
        if not self.username:
            self.username = self.email  # Optional: use email as username
        super().save(*args, **kwargs)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('on_leave', 'On Leave'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(default=timezone.now)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present'
    )
    notes = models.TextField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_employee_date'
            )
        ]
        ordering = ['-date', 'employee']
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payrolls'
    )
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    overtime_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    net_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pay_period_end', 'employee']
        verbose_name_plural = 'Payroll Records'

    def __str__(self):
        return f"{self.employee} - {self.pay_period_start} to {self.pay_period_end}"

    def save(self, *args, **kwargs):
        """Automatically calculate net pay before saving"""
        self.net_pay = (self.base_salary + 
                        self.overtime_pay + 
                        self.bonus - 
                        self.deductions)
        super().save(*args, **kwargs)

def clean(self):
    if self.pay_period_start >= self.pay_period_end:
        raise ValidationError("Pay period start must be before end date")
    
    if self.payment_date and self.payment_date < self.pay_period_end:
        raise ValidationError("Payment date cannot be before pay period end")