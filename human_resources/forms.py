# human_resources/forms.py
from django import forms
from .models import Attendance, Payroll, Employee, Training, LeaveApplication
from django.utils import timezone


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'status', 'notes']
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
            })
        }
        
        help_texts = {
            'employee': 'Select the employee for this attendance record',
            'date': 'Date of attendance (cannot be in the future)',
            'clock_in': 'Time when employee clocked in (24-hour format)',
            'clock_out': 'Time when employee clocked out (optional if still working)',
            'status': 'Current attendance status for this employee',
            'notes': 'Optional notes about this attendance record'
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
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
        
        # Filter employees to only active ones
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Add empty label for employee dropdown
        self.fields['employee'].empty_label = "Select an employee"
    
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
        fields = ['employee', 'pay_period_start', 'pay_period_end', 
                  'base_salary', 'overtime_pay', 'bonus', 'deductions',
                  'payment_date', 'status']
        widgets = {
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
            'deductions': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter employees to only active ones
        self.fields['employee'].queryset = Employee.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Add empty label for employee dropdown
        self.fields['employee'].empty_label = "Select an employee"


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'username',
            'position', 'hire_date', 'salary', 'qualifications', 'department', 'store',
            'manager', 'profile_image', 'is_active'
        ]
        widgets = {
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
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job position'
            }),
            'hire_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'qualifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List qualifications, certifications, and educational background'
            }),
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
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
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
            })
        }

        help_texts = {
            'leave_type': 'Select the type of leave you are applying for',
            'start_date': 'First day of leave',
            'end_date': 'Last day of leave',
            'reason': 'Optional: Provide details about your leave request'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields required
        self.fields['leave_type'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        self.fields['reason'].required = False

        # Set default start_date to today if creating new
        if not self.instance.pk:
            self.fields['start_date'].initial = timezone.now().date()

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
