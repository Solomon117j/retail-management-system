import uuid
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
from datetime import datetime as dt

class Employee(AbstractUser):
    # Primary key (replaces default 'id' field)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User type flags (required for compatibility with existing views)
    is_customer = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=True)

    # Personal info (override AbstractUser fields)
    first_name = models.CharField(_("first name"), max_length=50, blank=False)
    last_name = models.CharField(_("last name"), max_length=50, blank=False)
    email = models.EmailField(_("email address"), unique=True)  # Uncommented and made unique

    # Additional fields
    phone = models.CharField(_("phone number"), max_length=20, blank=True, null=True)

    # Personal Information
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    gender = models.CharField(
        _("gender"),
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say')
        ],
        blank=True,
        null=True
    )
    marital_status = models.CharField(
        _("marital status"),
        max_length=15,
        choices=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorced', 'Divorced'),
            ('widowed', 'Widowed'),
            ('separated', 'Separated')
        ],
        blank=True,
        null=True
    )
    nationality = models.CharField(_("nationality"), max_length=50, blank=True, null=True)

    # Address Information
    street_address = models.CharField(_("street address"), max_length=255, blank=True, null=True)
    city = models.CharField(_("city"), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_("postal code"), max_length=20, blank=True, null=True)
    country = models.CharField(_("country"), max_length=50, blank=True, null=True, default='Eswatini')

    # Emergency Contact
    emergency_contact_name = models.CharField(_("emergency contact name"), max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(_("emergency contact phone"), max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(_("emergency contact relationship"), max_length=50, blank=True, null=True)

    # Identification
    employee_id = models.CharField(_("employee ID"), max_length=20, unique=True, blank=True, null=True)
    national_id = models.CharField(_("national ID"), max_length=20, unique=True, blank=True, null=True)
    passport_number = models.CharField(_("passport number"), max_length=20, unique=True, blank=True, null=True)
    tax_id = models.CharField(_("tax ID"), max_length=20, unique=True, blank=True, null=True)

    # Employment Information
    hire_date = models.DateField(_("hire date"), blank=True, null=True)
    position = models.CharField(_("position"), max_length=50, blank=True)
    employment_type = models.CharField(
        _("employment type"),
        max_length=20,
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('temporary', 'Temporary'),
            ('intern', 'Intern')
        ],
        default='full_time'
    )
    contract_end_date = models.DateField(_("contract end date"), blank=True, null=True)
    probation_end_date = models.DateField(_("probation end date"), blank=True, null=True)
    work_schedule = models.CharField(_("work schedule"), max_length=50, blank=True, null=True)

    # Financial Information
    salary = models.DecimalField(
        _("salary"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Banking Information
    bank_name = models.CharField(_("bank name"), max_length=100, blank=True, null=True)
    account_number = models.CharField(_("account number"), max_length=30, blank=True, null=True)
    branch_code = models.CharField(_("branch code"), max_length=20, blank=True, null=True)

    # Skills and Qualifications
    qualifications = models.TextField(
        _("qualifications"),
        blank=True,
        null=True,
        help_text=_("List the employee's qualifications, certifications, and educational background")
    )
    skills = models.TextField(
        _("skills"),
        blank=True,
        null=True,
        help_text=_("List the employee's key skills and competencies")
    )
    languages_spoken = models.CharField(_("languages spoken"), max_length=255, blank=True, null=True)
    performance_rating = models.DecimalField(
        _("performance rating"),
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text=_("Performance rating on a scale of 1.0 to 5.0")
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

class Training(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='trainings'
    )
    training_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_completed = models.DateField()
    certification_status = models.CharField(max_length=100, blank=True, null=True)

    # Additional training fields
    provider = models.CharField(max_length=255, blank=True, null=True, verbose_name="Training Provider")
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name="Duration (Hours)",
        help_text="Duration of the training in hours"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Cost",
        help_text="Cost of the training in SZL"
    )
    certificate_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Certificate Number",
        help_text="Certificate or reference number"
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Expiry Date",
        help_text="Date when certification expires"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_completed']
        verbose_name = "Training Record"
        verbose_name_plural = "Training Records"

    def __str__(self):
        return f"{self.training_name} for {self.employee}"

class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('on_leave', 'On Leave'),
        ('sick_leave', 'Sick Leave'),
        ('vacational_leave', 'Vacational Leave'),
        ('maternity_leave', 'Maternity Leave'),
        ('study_leave', 'Study Leave'),
        ('compassionate_leave', 'Compassionate Leave'),
    ]

    CLOCK_METHOD_CHOICES = [
        ('manual', 'Manual Entry'),
        ('biometric', 'Biometric Scanner'),
        ('mobile_app', 'Mobile App'),
        ('web_portal', 'Web Portal'),
        ('card_reader', 'Card Reader'),
        ('other', 'Other'),
    ]

    SHIFT_TYPE_CHOICES = [
        ('morning', 'Morning Shift'),
        ('afternoon', 'Afternoon Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift'),
        ('overtime', 'Overtime'),
        ('flexible', 'Flexible Hours'),
        ('other', 'Other'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('auto_approved', 'Auto Approved'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
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

    # New comprehensive fields
    location = models.CharField(
        _("location"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Location where attendance was recorded (e.g., Main Office, Branch A)")
    )
    clock_method = models.CharField(
        _("clock method"),
        max_length=20,
        choices=CLOCK_METHOD_CHOICES,
        default='manual',
        help_text=_("Method used to record attendance")
    )
    shift_type = models.CharField(
        _("shift type"),
        max_length=20,
        choices=SHIFT_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text=_("Type of shift worked")
    )
    overtime_hours = models.DecimalField(
        _("overtime hours"),
        max_digits=4,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Additional hours worked beyond regular shift")
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendances',
        verbose_name=_("approved by"),
        help_text=_("Supervisor who approved this attendance record")
    )
    approval_status = models.CharField(
        _("approval status"),
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='auto_approved',
        help_text=_("Current approval status of the attendance record")
    )
    supervisor_notes = models.TextField(
        _("supervisor notes"),
        max_length=500,
        blank=True,
        null=True,
        help_text=_("Comments or notes from the approving supervisor")
    )

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

    @property
    def total_hours_worked(self):
        """Calculate total hours worked including overtime"""
        if self.clock_in and self.clock_out:
            # Calculate regular hours
            in_minutes = self.clock_in.hour * 60 + self.clock_in.minute
            out_minutes = self.clock_out.hour * 60 + self.clock_out.minute
            regular_minutes = out_minutes - in_minutes
            regular_hours = regular_minutes / 60.0

            # Add overtime hours
            return regular_hours + float(self.overtime_hours)
        return float(self.overtime_hours)

    @property
    def regular_hours_worked(self):
        """Calculate regular hours worked (clock in to clock out)"""
        if self.clock_in and self.clock_out:
            in_minutes = self.clock_in.hour * 60 + self.clock_in.minute
            out_minutes = self.clock_out.hour * 60 + self.clock_out.minute
            total_minutes = out_minutes - in_minutes
            return total_minutes / 60.0
        return 0.0


class Payroll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payrolls'
    )
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()

    # Basic Salary Components
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

    # Allowances
    housing_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Housing allowance amount"
    )
    transport_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Transport allowance amount"
    )
    medical_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Medical allowance amount"
    )
    meal_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Meal allowance amount"
    )
    other_allowances = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Other allowances"
    )

    # Taxes
    income_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Income tax amount"
    )
    social_security = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Social security contribution"
    )
    pension_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Pension fund contribution"
    )
    other_taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Other tax deductions"
    )

    # Benefits
    health_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Health insurance premium"
    )
    retirement_fund = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Retirement fund contribution"
    )

    # Additional Deductions
    loan_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Loan repayment deductions"
    )
    union_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Union or association fees"
    )
    other_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Other miscellaneous deductions"
    )

    # Legacy deductions field (for backward compatibility)
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="General deductions (legacy field)"
    )

    # Payment Details
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='bank_transfer',
        help_text="Method of payment"
    )
    bank_reference = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Bank reference or transaction ID"
    )
    currency = models.CharField(
        max_length=3,
        default='SZL',
        help_text="Currency code (e.g., SZL, USD)"
    )

    # Calculation Fields
    regular_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Regular working hours in pay period"
    )
    taxable_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Taxable income amount"
    )
    gross_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total gross income"
    )

    # Final Calculations
    net_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Final net pay amount"
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

    @property
    def total_allowances(self):
        """Calculate total allowances"""
        return (self.housing_allowance + self.transport_allowance +
                self.medical_allowance + self.meal_allowance + self.other_allowances)

    @property
    def total_taxes(self):
        """Calculate total tax deductions"""
        return self.income_tax + self.social_security + self.pension_contribution + self.other_taxes

    @property
    def total_benefits(self):
        """Calculate total benefits"""
        return self.health_insurance + self.retirement_fund

    @property
    def total_additional_deductions(self):
        """Calculate total additional deductions"""
        return self.loan_deductions + self.union_fees + self.other_deductions

    @property
    def gross_pay(self):
        """Calculate gross pay as base salary + overtime + bonus + allowances"""
        return self.base_salary + self.overtime_pay + self.bonus + self.total_allowances

    @property
    def total_deductions(self):
        """Calculate total deductions including taxes and benefits"""
        return (self.deductions + self.total_taxes + self.total_additional_deductions +
                self.total_benefits)

    def save(self, *args, **kwargs):
        """Automatically calculate comprehensive payroll amounts before saving"""
        # Calculate gross income
        self.gross_income = self.gross_pay

        # Calculate taxable income (gross minus certain allowances if applicable)
        # For simplicity, taxable income = gross income, but can be customized
        self.taxable_income = self.gross_income

        # Calculate net pay
        self.net_pay = self.gross_income - self.total_deductions

        super().save(*args, **kwargs)

    def clean(self):
        if self.pay_period_start >= self.pay_period_end:
            raise ValidationError("Pay period start must be before end date")

        if self.payment_date and self.payment_date < self.pay_period_end:
            raise ValidationError("Payment date cannot be before pay period end")

class CostCenter(models.Model):
    """Cost centers for enterprise cost tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(_("cost center code"), max_length=20, unique=True)
    name = models.CharField(_("cost center name"), max_length=100)
    description = models.TextField(
        _("description"),
        blank=True,
        null=True,
        help_text=_("Description of this cost center")
    )
    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_cost_centers',
        verbose_name=_("cost center manager"),
        help_text=_("Manager responsible for this cost center")
    )
    budget = models.DecimalField(
        _("annual budget"),
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Annual budget for this cost center")
    )
    is_active = models.BooleanField(_("active"), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = _("Cost Center")
        verbose_name_plural = _("Cost Centers")

    def __str__(self):
        return f"{self.code} - {self.name}"


class Shift(models.Model):
    """Predefined shift templates that can be assigned to employees"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    SHIFT_TYPE_CHOICES = [
        ('morning', 'Morning Shift'),
        ('afternoon', 'Afternoon Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift'),
        ('weekend', 'Weekend Shift'),
        ('holiday', 'Holiday Shift'),
        ('overtime', 'Overtime Shift'),
        ('flexible', 'Flexible Hours'),
        ('other', 'Other'),
    ]

    name = models.CharField(_("shift name"), max_length=100, unique=True)
    shift_type = models.CharField(
        _("shift type"),
        max_length=20,
        choices=SHIFT_TYPE_CHOICES,
        default='morning'
    )
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"))
    duration_hours = models.DecimalField(
        _("duration hours"),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Duration in hours (auto-calculated)")
    )
    description = models.TextField(
        _("description"),
        blank=True,
        null=True,
        help_text=_("Optional description of the shift")
    )
    is_active = models.BooleanField(_("active"), default=True)

    # Enterprise-ready fields
    break_times = models.JSONField(
        _("break times"),
        blank=True,
        null=True,
        help_text=_("Break schedule in JSON format: [{'start': '10:00', 'end': '10:15', 'type': 'lunch'}, ...]")
    )
    overtime_rules = models.TextField(
        _("overtime rules"),
        blank=True,
        null=True,
        help_text=_("Rules for overtime calculation and approval")
    )
    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shifts',
        verbose_name=_("cost center"),
        help_text=_("Cost center this shift belongs to")
    )
    approval_required = models.BooleanField(
        _("approval required"),
        default=False,
        help_text=_("Whether this shift requires approval before assignment")
    )
    approval_levels = models.PositiveIntegerField(
        _("approval levels"),
        default=1,
        help_text=_("Number of approval levels required")
    )

    # Store and department restrictions
    allowed_stores = models.ManyToManyField(
        'store_management.Store',
        blank=True,
        related_name='allowed_shifts',
        verbose_name=_("allowed stores"),
        help_text=_("Stores where this shift can be used (leave empty for all stores)")
    )
    allowed_departments = models.ManyToManyField(
        'store_management.Department',
        blank=True,
        related_name='allowed_shifts',
        verbose_name=_("allowed departments"),
        help_text=_("Departments where this shift can be used (leave empty for all departments)")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Shift Template")
        verbose_name_plural = _("Shift Templates")

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

    def save(self, *args, **kwargs):
        # Auto-calculate duration
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            if end_minutes >= start_minutes:
                duration_minutes = end_minutes - start_minutes
            else:
                # Handle overnight shifts
                duration_minutes = (24 * 60 - start_minutes) + end_minutes
            self.duration_hours = round(duration_minutes / 60.0, 2)
        super().save(*args, **kwargs)

    @property
    def total_break_duration(self):
        """Calculate total break time in hours"""
        if not self.break_times:
            return 0.0

        total_minutes = 0
        try:
            breaks = json.loads(self.break_times) if isinstance(self.break_times, str) else self.break_times
            for break_info in breaks:
                if 'start' in break_info and 'end' in break_info:
                    start = break_info['start']
                    end = break_info['end']
                    if isinstance(start, str) and isinstance(end, str):
                        start_time = dt.strptime(start, '%H:%M').time()
                        end_time = dt.strptime(end, '%H:%M').time()
                        start_minutes = start_time.hour * 60 + start_time.minute
                        end_minutes = end_time.hour * 60 + end_time.minute
                        if end_minutes >= start_minutes:
                            total_minutes += end_minutes - start_minutes
                        else:
                            # Handle overnight breaks (unlikely but possible)
                            total_minutes += (24 * 60 - start_minutes) + end_minutes
        except (json.JSONDecodeError, ValueError, KeyError):
            return 0.0

        return round(total_minutes / 60.0, 2)


class Schedule(models.Model):
    """Employee work schedules - assigns shifts to employees on specific dates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    date = models.DateField(_("scheduled date"))
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    # Override shift times if needed
    custom_start_time = models.TimeField(
        _("custom start time"),
        blank=True,
        null=True,
        help_text=_("Override the shift's start time")
    )
    custom_end_time = models.TimeField(
        _("custom end time"),
        blank=True,
        null=True,
        help_text=_("Override the shift's end time")
    )

    # Additional schedule information
    notes = models.TextField(
        _("notes"),
        blank=True,
        null=True,
        help_text=_("Additional notes about this schedule")
    )
    assigned_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_schedules',
        verbose_name=_("assigned by"),
        help_text=_("Supervisor who assigned this schedule")
    )

    # Actual vs scheduled tracking
    actual_start_time = models.TimeField(
        _("actual start time"),
        blank=True,
        null=True,
        help_text=_("Actual time employee started work")
    )
    actual_end_time = models.TimeField(
        _("actual end time"),
        blank=True,
        null=True,
        help_text=_("Actual time employee ended work")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'employee']
        verbose_name = _("Employee Schedule")
        verbose_name_plural = _("Employee Schedules")
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_employee_date_schedule'
            )
        ]

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.shift.name})"

    @property
    def effective_start_time(self):
        """Return custom start time if set, otherwise shift start time"""
        return self.custom_start_time or self.shift.start_time

    @property
    def effective_end_time(self):
        """Return custom end time if set, otherwise shift end time"""
        return self.custom_end_time or self.shift.end_time

    @property
    def scheduled_duration_hours(self):
        """Calculate scheduled duration in hours"""
        if self.effective_start_time and self.effective_end_time:
            start_minutes = self.effective_start_time.hour * 60 + self.effective_start_time.minute
            end_minutes = self.effective_end_time.hour * 60 + self.effective_end_time.minute
            if end_minutes >= start_minutes:
                duration_minutes = end_minutes - start_minutes
            else:
                # Handle overnight shifts
                duration_minutes = (24 * 60 - start_minutes) + end_minutes
            return round(duration_minutes / 60.0, 2)
        return 0.0

    @property
    def actual_duration_hours(self):
        """Calculate actual worked duration in hours"""
        if self.actual_start_time and self.actual_end_time:
            start_minutes = self.actual_start_time.hour * 60 + self.actual_start_time.minute
            end_minutes = self.actual_end_time.hour * 60 + self.actual_end_time.minute
            if end_minutes >= start_minutes:
                duration_minutes = end_minutes - start_minutes
            else:
                # Handle overnight shifts
                duration_minutes = (24 * 60 - start_minutes) + end_minutes
            return round(duration_minutes / 60.0, 2)
        return 0.0

    def clean(self):
        if self.date and self.date < timezone.now().date():
            raise ValidationError("Cannot schedule for past dates.")

        # Check if employee is active
        if self.employee and not self.employee.is_active:
            raise ValidationError("Cannot schedule inactive employees.")

        # Check if shift is active
        if self.shift and not self.shift.is_active:
            raise ValidationError("Cannot assign inactive shifts.")

        # Check store/department restrictions
        if self.shift and self.shift.allowed_stores.exists() and self.employee and self.employee.store not in self.shift.allowed_stores.all():
            raise ValidationError(f"This shift is not allowed for the employee's store ({self.employee.store}).")

        if self.shift and self.shift.allowed_departments.exists() and self.employee and self.employee.department not in self.shift.allowed_departments.all():
            raise ValidationError(f"This shift is not allowed for the employee's department ({self.employee.department}).")


class LeaveApplication(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('sick_leave', 'Sick Leave'),
        ('vacational_leave', 'Vacational Leave'),
        ('maternity_leave', 'Maternity Leave'),
        ('study_leave', 'Study Leave'),
        ('compassionate_leave', 'Compassionate Leave'),
        ('annual_leave', 'Annual Leave'),
        ('unpaid_leave', 'Unpaid Leave'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_applications'
    )
    leave_type = models.CharField(
        max_length=30,
        choices=LEAVE_TYPE_CHOICES,
        default='annual_leave'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_applications'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = _("Leave Application")
        verbose_name_plural = _("Leave Applications")

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def leave_days(self):
        """Calculate the number of leave days (inclusive of start and end dates)"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before or equal to end date.")
        if self.start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past.")
