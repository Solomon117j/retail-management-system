from django import forms
from .models import Attendance, Payroll, Employee, Training, LeaveApplication, Shift
from django.utils import timezone


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'status', 'notes',
                  'location', 'clock_method', 'shift_type', 'overtime_hours',
                  'approved_by', 'approval_status', 'supervisor_notes']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'clock_in': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '60'  # 1-minute intervals
            }),
            'clock_out': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '60'  # 1-minute intervals
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any notes about this attendance record (optional)',
                'maxlength': 200
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Main Office, Branch A, Remote',
                'maxlength': 100
            }),
            'clock_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'shift_type': forms.Select(attrs={
                'class': 'form-select shift-type-select'
            }),
            'overtime_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',
                'min': '0',
                'placeholder': '0.00'
            }),
            'approved_by': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'approval_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supervisor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Supervisor comments or approval notes',
                'maxlength': 500
            })
        }

        help_texts = {
            'employee': 'Select the employee for this attendance record',
            'date': 'Date of attendance (cannot be in the future)',
            'clock_in': 'Time when employee clocked in (24-hour format)',
            'clock_out': 'Time when employee clocked out (optional if still working)',
            'status': 'Current attendance status for this employee',
            'notes': 'Optional notes about this attendance record',
            'location': 'Location where attendance was recorded (e.g., Main Office, Branch A)',
            'clock_method': 'Method used to record attendance',
            'shift_type': 'Type of shift worked',
            'overtime_hours': 'Additional hours worked beyond regular shift',
            'approved_by': 'Supervisor who approved this attendance record',
            'approval_status': 'Current approval status of the attendance record',
            'supervisor_notes': 'Comments or notes from the approving supervisor'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields required
        self.fields['employee'].required = True
        self.fields['date'].required = True
        self.fields['status'].required = True

        # Make clock times optional (can be added later)
        self.fields['clock_in'].required = False
        self.fields['clock_out'].required = False
        self.fields['notes'].required = False

        # Make new fields optional
        self.fields['location'].required = False
        self.fields['shift_type'].required = False
        self.fields['overtime_hours'].required = False
        self.fields['approved_by'].required = False
        self.fields['supervisor_notes'].required = False

        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()

        # Filter employees to only active ones
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')

        # Filter approved_by to employees who are managers/supervisors (have subordinates)
        self.fields['approved_by'].queryset = Employee.objects.filter(
            is_active=True,
            subordinates__isnull=False
        ).distinct().order_by('first_name', 'last_name')

        # Add empty labels for dropdowns
        self.fields['employee'].empty_label = "Select an employee"
        self.fields['approved_by'].empty_label = "Select supervisor (optional)"
    
    def clean_date(self):
        """Validate that date is not in the future"""
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError(
                'Attendance date cannot be in the future'
            )
        return date
    
    def clean_clock_out(self):
        """Validate that clock out is after clock in"""
        clock_in = self.cleaned_data.get('clock_in')
        clock_out = self.cleaned_data.get('clock_out')

        if clock_in and clock_out:
            if clock_out <= clock_in:
                raise forms.ValidationError(
                    'Clock out time must be after clock in time'
                )

        return clock_out

    def clean_overtime_hours(self):
        """Validate that overtime hours is not negative"""
        overtime_hours = self.cleaned_data.get('overtime_hours')
        if overtime_hours is not None and overtime_hours < 0:
            raise forms.ValidationError(
                'Overtime hours cannot be negative'
            )
        return overtime_hours
    
    def clean(self):
        """Cross-field validation and duplicate check"""
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        date = cleaned_data.get('date')
        status = cleaned_data.get('status')
        clock_in = cleaned_data.get('clock_in')
        clock_out = cleaned_data.get('clock_out')
        
        # Check for duplicate attendance records
        if employee and date:
            existing_attendance = Attendance.objects.filter(
                employee=employee,
                date=date
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_attendance.exists():
                raise forms.ValidationError(
                    f'Attendance record already exists for {employee.get_full_name()} on {date}. '
                    f'Please update the existing record instead.'
                )
        
        # If status is 'present', require clock_in
        if status == 'present' and not clock_in:
            raise forms.ValidationError(
                'Clock in time is required when status is "Present"'
            )
        
        # If status is 'absent' or 'on_leave' or any leave type, clock times should be empty
        leave_statuses = ['absent', 'on_leave', 'sick_leave', 'vacational_leave', 'maternity_leave', 'study_leave', 'compassionate_leave']
        if status in leave_statuses:
            if clock_in or clock_out:
                raise forms.ValidationError(
                    'Clock times should not be set when employee is absent or on leave'
                )
        
        return cleaned_data


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            # Basic Information
            'employee', 'pay_period_start', 'pay_period_end',

            # Basic Salary Components
            'base_salary', 'overtime_pay', 'bonus',

            # Allowances
            'housing_allowance', 'transport_allowance', 'medical_allowance',
            'meal_allowance', 'other_allowances',

            # Taxes
            'income_tax', 'social_security', 'pension_contribution', 'other_taxes',

            # Benefits
            'health_insurance', 'retirement_fund',

            # Additional Deductions
            'loan_deductions', 'union_fees', 'other_deductions',

            # Legacy deductions field (for backward compatibility)
            'deductions',

            # Payment Details
            'payment_method', 'bank_reference', 'currency',

            # Calculation Fields
            'regular_hours', 'taxable_income', 'gross_income',

            # Final Details
            'payment_date', 'status'
        ]

        widgets = {
            # Basic Information
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'pay_period_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'pay_period_end': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),

            # Basic Salary Components
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'overtime_pay': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'bonus': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),

            # Allowances
            'housing_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'transport_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'medical_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'meal_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'other_allowances': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),

            # Taxes
            'income_tax': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'social_security': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'pension_contribution': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'other_taxes': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),

            # Benefits
            'health_insurance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'retirement_fund': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),

            # Additional Deductions
            'loan_deductions': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'union_fees': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'other_deductions': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),

            # Legacy deductions field
            'deductions': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),

            # Payment Details
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'bank_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank reference or transaction ID',
                'maxlength': 50
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., SZL, USD',
                'maxlength': 3,
                'value': 'SZL'
            }),

            # Calculation Fields
            'regular_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'taxable_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'readonly': True
            }),
            'gross_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'readonly': True
            }),

            # Final Details
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

        help_texts = {
            # Basic Information
            'employee': 'Select the employee for this payroll record',
            'pay_period_start': 'Start date of the pay period',
            'pay_period_end': 'End date of the pay period',

            # Basic Salary Components
            'base_salary': 'Employee\'s base salary for this pay period',
            'overtime_pay': 'Additional pay for overtime hours worked',
            'bonus': 'Any bonus payments for this pay period',

            # Allowances
            'housing_allowance': 'Housing allowance amount',
            'transport_allowance': 'Transport allowance amount',
            'medical_allowance': 'Medical allowance amount',
            'meal_allowance': 'Meal allowance amount',
            'other_allowances': 'Other miscellaneous allowances',

            # Taxes
            'income_tax': 'Income tax amount to be deducted',
            'social_security': 'Social security contribution',
            'pension_contribution': 'Pension fund contribution',
            'other_taxes': 'Other tax deductions',

            # Benefits
            'health_insurance': 'Health insurance premium',
            'retirement_fund': 'Retirement fund contribution',

            # Additional Deductions
            'loan_deductions': 'Loan repayment deductions',
            'union_fees': 'Union or association fees',
            'other_deductions': 'Other miscellaneous deductions',

            # Legacy deductions field
            'deductions': 'General deductions (legacy field)',

            # Payment Details
            'payment_method': 'Method used for payment',
            'bank_reference': 'Bank reference or transaction ID',
            'currency': 'Currency code (e.g., SZL, USD)',

            # Calculation Fields
            'regular_hours': 'Regular working hours in this pay period',
            'taxable_income': 'Calculated taxable income (auto-calculated)',
            'gross_income': 'Calculated gross income (auto-calculated)',

            # Final Details
            'payment_date': 'Date when payment was made',
            'status': 'Current status of this payroll record'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter employees to only active ones
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')

        # Add empty label for employee dropdown
        self.fields['employee'].empty_label = "Select an employee"

        # Make most fields optional (will be calculated or entered as needed)
        optional_fields = [
            'overtime_pay', 'bonus',
            'housing_allowance', 'transport_allowance', 'medical_allowance',
            'meal_allowance', 'other_allowances',
            'income_tax', 'social_security', 'pension_contribution', 'other_taxes',
            'health_insurance', 'retirement_fund',
            'loan_deductions', 'union_fees', 'other_deductions',
            'deductions', 'bank_reference', 'regular_hours', 'payment_date'
        ]

        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

        # Set default currency
        if not self.instance.pk:
            self.fields['currency'].initial = 'SZL'

    def clean_pay_period_end(self):
        """Validate that pay period end is after start"""
        pay_period_end = self.cleaned_data.get('pay_period_end')
        pay_period_start = self.cleaned_data.get('pay_period_start')

        if pay_period_end and pay_period_start and pay_period_end <= pay_period_start:
            raise forms.ValidationError(
                'Pay period end must be after the start date'
            )
        return pay_period_end

    def clean_payment_date(self):
        """Validate that payment date is not before pay period end"""
        payment_date = self.cleaned_data.get('payment_date')
        pay_period_end = self.cleaned_data.get('pay_period_end')

        if payment_date and pay_period_end and payment_date < pay_period_end:
            raise forms.ValidationError(
                'Payment date cannot be before pay period end'
            )
        return payment_date


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            # Basic Information
            'first_name', 'last_name', 'email', 'phone', 'username',

            # Personal Information
            'date_of_birth', 'gender', 'marital_status', 'nationality',

            # Address Information
            'street_address', 'city', 'postal_code', 'country',

            # Emergency Contact
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',

            # Identification
            'employee_id', 'national_id', 'passport_number', 'tax_id',

            # Employment Information
            'position', 'hire_date', 'employment_type', 'contract_end_date',
            'probation_end_date', 'work_schedule', 'salary',

            # Banking Information
            'bank_name', 'account_number', 'branch_code',

            # Skills and Qualifications
            'qualifications', 'skills', 'languages_spoken', 'performance_rating',

            # Relationships
            'department', 'store', 'manager', 'profile_image', 'is_active'
        ]
        widgets = {
            # Basic Information
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username for login'
            }),

            # Personal Information
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nationality'
            }),

            # Address Information
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter postal code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter country',
                'value': 'Eswatini'
            }),

            # Emergency Contact
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter emergency contact phone'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Parent, Spouse, Sibling'
            }),

            # Identification
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee ID'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter national ID number'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter passport number'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tax ID number'
            }),

            # Employment Information
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job position'
            }),
            'hire_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'probation_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'work_schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monday-Friday 8AM-5PM'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),

            # Banking Information
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank name'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account number'
            }),
            'branch_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch code'
            }),

            # Skills and Qualifications
            'qualifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List qualifications, certifications, and educational background'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List key skills and competencies'
            }),
            'languages_spoken': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., English, siSwati, Afrikaans'
            }),
            'performance_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '1.0',
                'max': '5.0',
                'placeholder': '1.0 - 5.0'
            }),

            # Relationships
            'department': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'store': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make username optional for existing employees
        if self.instance.pk:
            self.fields['username'].required = False
        else:
            self.fields['username'].required = True
        
        # Filter managers to only active employees
        self.fields['manager'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Add empty labels for dropdowns
        self.fields['department'].empty_label = "Select department (optional)"
        self.fields['store'].empty_label = "Select store (optional)"
        self.fields['manager'].empty_label = "Select manager (optional)"
        
        # Make profile image optional
        self.fields['profile_image'].required = False


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = [
            'employee', 'training_name', 'description', 'date_completed', 'certification_status',
            'provider', 'duration_hours', 'cost', 'certificate_number', 'expiry_date'
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'training_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter training name or course title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the training content, objectives, and key topics covered'
            }),
            'date_completed': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'certification_status': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Certified, Completed, In Progress, Failed'
            }),
            'provider': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter training provider'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Duration in hours'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Cost in SZL'
            }),
            'certificate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Certificate or reference number'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

        help_texts = {
            'employee': 'Select the employee who completed this training',
            'training_name': 'Name of the training program or course',
            'description': 'Detailed description of the training content',
            'date_completed': 'Date when the training was completed',
            'certification_status': 'Certification or completion status',
            'provider': 'Training provider or organization',
            'duration_hours': 'Duration of the training in hours',
            'cost': 'Cost of the training in SZL',
            'certificate_number': 'Certificate or reference number',
            'expiry_date': 'Date when certification expires',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields required
        self.fields['employee'].required = True
        self.fields['training_name'].required = True
        self.fields['date_completed'].required = True

        # Make description and certification_status optional
        self.fields['description'].required = False
        self.fields['certification_status'].required = False
        self.fields['provider'].required = False
        self.fields['duration_hours'].required = False
        self.fields['cost'].required = False
        self.fields['certificate_number'].required = False
        self.fields['expiry_date'].required = False

        # Set default date to today if creating new
        if not self.instance.pk:
            self.fields['date_completed'].initial = timezone.now().date()

        # Filter employees to only active ones
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')

        # Add empty label for employee dropdown
        self.fields['employee'].empty_label = "Select an employee"

    def clean_date_completed(self):
        """Validate that date is not in the future"""
        date = self.cleaned_data.get('date_completed')
        if date and date > timezone.now().date():
            raise forms.ValidationError(
                'Training completion date cannot be in the future'
            )
        return date


class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'approved_by']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'leave_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide a reason for your leave application'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'approved_by': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            })
        }

        help_texts = {
            'employee': 'Select the employee applying for leave',
            'leave_type': 'Select the type of leave you are applying for',
            'start_date': 'First day of leave',
            'end_date': 'Last day of leave',
            'reason': 'Optional: Provide details about your leave request',
            'status': 'Current approval status of the leave application',
            'approved_by': 'Supervisor who approved this leave application'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields required
        self.fields['employee'].required = True
        self.fields['leave_type'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        self.fields['reason'].required = False
        self.fields['status'].required = False
        self.fields['approved_by'].required = False

        # Set default start_date to today if creating new
        if not self.instance.pk:
            self.fields['start_date'].initial = timezone.now().date()
            self.fields['status'].initial = 'pending'

        # Filter employees to only active ones
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')

        # Filter approved_by to employees who are managers/supervisors (have subordinates)
        self.fields['approved_by'].queryset = Employee.objects.filter(
            is_active=True,
            subordinates__isnull=False
        ).distinct().order_by('first_name', 'last_name')

        # Add empty labels for dropdowns
        self.fields['employee'].empty_label = "Select an employee"
        self.fields['approved_by'].empty_label = "Select supervisor (optional)"

    def clean_start_date(self):
        """Validate that start date is not in the past"""
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError(
                'Leave start date cannot be in the past'
            )
        return start_date

    def clean_end_date(self):
        """Validate that end date is after start date"""
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError(
                'Leave end date must be after or equal to start date'
            )
        return end_date


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = [
            'name', 'shift_type', 'start_time', 'end_time', 'description',
            'break_times', 'overtime_rules', 'cost_center', 'approval_required',
            'approval_levels', 'allowed_stores', 'allowed_departments', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control shift-name-input',
                'placeholder': 'Enter a unique and descriptive name for this shift'
            }),
            'shift_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control shift-time-input'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control shift-time-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control shift-description-textarea',
                'rows': 4,
                'placeholder': 'Provide a detailed description of this shift, including responsibilities, special requirements, or notes for employees...'
            }),
            'break_times': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Break schedule in JSON format: [{"start": "10:00", "end": "10:15", "type": "lunch"}, ...]'
            }),
            'overtime_rules': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Rules for overtime calculation and approval'
            }),
            'cost_center': forms.Select(attrs={
                'class': 'form-select'
            }),
            'approval_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'approval_levels': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Number of approval levels'
            }),
            'allowed_stores': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'allowed_departments': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        help_texts = {
            'name': 'Unique name for this shift template',
            'shift_type': 'Type of shift (morning, afternoon, etc.)',
            'start_time': 'Start time of the shift',
            'end_time': 'End time of the shift',
            'description': 'Optional description of the shift',
            'break_times': 'Break schedule in JSON format',
            'overtime_rules': 'Rules for overtime calculation and approval',
            'cost_center': 'Cost center this shift belongs to',
            'approval_required': 'Whether this shift requires approval before assignment',
            'approval_levels': 'Number of approval levels required',
            'allowed_stores': 'Stores where this shift can be used (leave empty for all stores)',
            'allowed_departments': 'Departments where this shift can be used (leave empty for all departments)',
            'is_active': 'Whether this shift is active and available for use'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields required
        self.fields['name'].required = True
        self.fields['shift_type'].required = True
        self.fields['start_time'].required = True
        self.fields['end_time'].required = True

        # Make optional fields
        self.fields['description'].required = False
        self.fields['break_times'].required = False
        self.fields['overtime_rules'].required = False
        self.fields['cost_center'].required = False
        self.fields['approval_required'].required = False
        self.fields['approval_levels'].required = False
        self.fields['allowed_stores'].required = False
        self.fields['allowed_departments'].required = False
        self.fields['is_active'].required = False

        # Set default values
        if not self.instance.pk:
            self.fields['is_active'].initial = True
            self.fields['approval_levels'].initial = 1

        # Add empty labels for dropdowns
        self.fields['cost_center'].empty_label = "Select cost center (optional)"

    def clean_name(self):
        """Validate that shift name is unique"""
        name = self.cleaned_data.get('name')
        if name:
            existing_shift = Shift.objects.filter(name=name).exclude(pk=self.instance.pk if self.instance else None)
            if existing_shift.exists():
                raise forms.ValidationError(
                    'A shift with this name already exists'
                )
        return name

    def clean_end_time(self):
        """Validate that end time is after start time"""
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')

        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError(
                'End time must be after start time'
            )
        return end_time

    def clean_break_times(self):
        """Validate break_times JSON format"""
        break_times = self.cleaned_data.get('break_times')
        if break_times:
            try:
                import json
                breaks = json.loads(break_times)
                if not isinstance(breaks, list):
                    raise forms.ValidationError(
                        'Break times must be a JSON array'
                    )
                for break_info in breaks:
                    if not isinstance(break_info, dict):
                        raise forms.ValidationError(
                            'Each break must be a JSON object'
                        )
                    if 'start' not in break_info or 'end' not in break_info:
                        raise forms.ValidationError(
                            'Each break must have start and end times'
                        )
            except (json.JSONDecodeError, ValueError):
                raise forms.ValidationError(
                    'Invalid JSON format for break times'
                )
        return break_times

    def clean_approval_levels(self):
        """Validate approval levels"""
        approval_levels = self.cleaned_data.get('approval_levels')
        if approval_levels is not None and approval_levels < 1:
            raise forms.ValidationError(
                'Approval levels must be at least 1'
            )
        return approval_levels
