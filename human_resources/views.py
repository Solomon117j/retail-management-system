# from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from .models import Attendance, Payroll, Employee, Training, LeaveApplication, Shift, Schedule
from .forms import AttendanceForm, PayrollForm, EmployeeForm, TrainingForm, LeaveApplicationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib import messages
from django.shortcuts import get_object_or_404

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
import csv
try:
    import pandas as pd
except Exception:
    pd = None
from io import BytesIO

# human_resources/views.py

# Employee Views
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'human_resources/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        queryset = Employee.objects.select_related('store', 'department', 'manager')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(position__icontains=search) |
                Q(username__icontains=search)
            )
        
        # Filter by store
        store_id = self.request.GET.get('store')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        # Filter by department
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('last_name', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Import here to avoid circular imports
        from store_management.models import Store, Department
        
        context['stores'] = Store.objects.all()
        context['departments'] = Department.objects.all()
        
        # Add statistics
        context['total_employees'] = Employee.objects.count()
        context['active_employees'] = Employee.objects.filter(is_active=True).count()
        context['inactive_employees'] = Employee.objects.filter(is_active=False).count()
        context['employees_with_salary'] = Employee.objects.filter(salary__isnull=False).count()
        
        return context

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'human_resources/employee_detail.html'
    context_object_name = 'employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add recent attendance and payroll records
        context['recent_attendance'] = self.object.attendances.all()[:10]
        context['recent_payroll'] = self.object.payrolls.all()[:5]
        # Add subordinates
        context['subordinates'] = Employee.objects.filter(manager=self.object)
        # Add statistics
        context['total_attendance'] = self.object.attendances.count()
        context['total_payroll'] = self.object.payrolls.count()
        context['subordinate_count'] = Employee.objects.filter(manager=self.object).count()
        return context

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'human_resources/employee_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Import here to avoid circular imports
        from store_management.models import Store, Department
        
        context['stores'] = Store.objects.all()
        context['departments'] = Department.objects.all()
        context['managers'] = Employee.objects.filter(
            Q(position__icontains='manager') | Q(position__icontains='supervisor')
        )
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Employee {form.instance.get_full_name()} created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('hr:employee_detail', kwargs={'pk': self.object.pk})

class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'human_resources/employee_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Import here to avoid circular imports
        from store_management.models import Store, Department
        
        context['stores'] = Store.objects.all()
        context['departments'] = Department.objects.all()
        context['managers'] = Employee.objects.filter(
            Q(position__icontains='manager') | Q(position__icontains='supervisor')
        ).exclude(pk=self.object.pk)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Employee {form.instance.get_full_name()} updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('hr:employee_detail', kwargs={'pk': self.object.pk})

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'human_resources/employee_confirm_delete.html'
    success_url = reverse_lazy('hr:employee_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related data counts for impact analysis
        context['attendance_count'] = self.object.attendances.count()
        context['payroll_count'] = self.object.payrolls.count()
        context['subordinate_count'] = Employee.objects.filter(manager=self.object).count()
        context['subordinates'] = Employee.objects.filter(manager=self.object)
        return context
    
    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        messages.success(request, f'Employee {employee.get_full_name()} deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Attendance Views
class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'human_resources/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee', 'approved_by', 'employee__store', 'employee__department')
        # Filter by employee if requested
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by approval_status
        approval_status = self.request.GET.get('approval_status')
        if approval_status:
            queryset = queryset.filter(approval_status=approval_status)

        # Filter by shift_type
        shift_type = self.request.GET.get('shift_type')
        if shift_type:
            queryset = queryset.filter(shift_type=shift_type)

        # Filter by location
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by clock_method
        clock_method = self.request.GET.get('clock_method')
        if clock_method:
            queryset = queryset.filter(clock_method=clock_method)

        # Filter by approved_by
        approved_by_id = self.request.GET.get('approved_by')
        if approved_by_id:
            queryset = queryset.filter(approved_by_id=approved_by_id)

        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate statistics based on the current queryset (what's actually displayed)
        queryset = self.get_queryset()

        # Count by status from the current filtered queryset
        status_counts = {}
        for attendance in queryset:
            status = attendance.status
            status_counts[status] = status_counts.get(status, 0) + 1

        context['present_today_count'] = status_counts.get('present', 0)
        context['late_today_count'] = status_counts.get('late', 0)
        context['absent_today_count'] = status_counts.get('absent', 0)
        context['on_leave_today_count'] = status_counts.get('on_leave', 0)
        context['sick_leave_today_count'] = status_counts.get('sick_leave', 0)
        context['vacational_leave_today_count'] = status_counts.get('vacational_leave', 0)
        context['maternity_leave_today_count'] = status_counts.get('maternity_leave', 0)
        context['study_leave_today_count'] = status_counts.get('study_leave', 0)
        context['compassionate_leave_today_count'] = status_counts.get('compassionate_leave', 0)

        return context

# HTMX Quick Add Attendance
@login_required
def attendance_quick_add(request):
    """HTMX endpoint for quick attendance add modal/form."""
    from django.shortcuts import render
    
    if request.method == 'GET':
        # Return the form fragment for HTMX modal
        form = AttendanceForm()
        employees = Employee.objects.filter(is_active=True).order_by('last_name', 'first_name')
        return render(request, 'partials/attendance_quick_add_modal.html', {
            'form': form,
            'employees': employees
        })
    
    elif request.method == 'POST':
        # Handle form submission via HTMX
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            return render(request, 'partials/attendance_added_success.html', {
                'employee': attendance.employee
            })
        else:
            # Return form with errors
            employees = Employee.objects.filter(is_active=True).order_by('last_name', 'first_name')
            return render(request, 'partials/attendance_quick_add_modal.html', {
                'form': form,
                'employees': employees
            }, status=400)

class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'human_resources/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        try:
            # Check if this is an AJAX request
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                attendance = form.save()
                return JsonResponse({
                    'success': True,
                    'id': str(attendance.id),
                    'message': f'Attendance record for {attendance.employee.get_full_name()} saved successfully!'
                })
            else:
                return super().form_valid(form)
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {
                            '__all__': ['Attendance record already exists for this employee on the selected date. Please update the existing record instead.']
                        }
                    }, status=400)
                else:
                    messages.error(
                        self.request,
                        'Attendance record already exists for this employee on the selected date. '
                        'Please update the existing record instead.'
                    )
                    return self.form_invalid(form)
            else:
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': ['An error occurred while saving the attendance record.']}
                    }, status=500)
                else:
                    raise e

    def form_invalid(self, form):
        # Check if this is an AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        else:
            return super().form_invalid(form)

class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'human_resources/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        try:
            # Check if this is an AJAX request
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                attendance = form.save()
                return JsonResponse({
                    'success': True,
                    'id': str(attendance.id),
                    'message': f'Attendance record for {attendance.employee.get_full_name()} updated successfully!'
                })
            else:
                return super().form_valid(form)
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['An error occurred while updating the attendance record.']}
                }, status=500)
            else:
                raise e

    def form_invalid(self, form):
        # Check if this is an AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        else:
            return super().form_invalid(form)

class AttendanceDetailView(LoginRequiredMixin, DetailView):
    model = Attendance
    template_name = 'human_resources/attendance_detail.html'

class AttendanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Attendance
    template_name = 'human_resources/attendance_confirm_delete.html'
    success_url = reverse_lazy('hr:attendance_list')

# Payroll Views
class PayrollListView(LoginRequiredMixin, ListView):
    model = Payroll
    template_name = 'human_resources/payroll_list.html'
    context_object_name = 'payrolls'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by employee or status
        employee_id = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-pay_period_end')

class PayrollCreateView(LoginRequiredMixin, CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'human_resources/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def form_valid(self, form):
        try:
            # Check if this is an AJAX request
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                payroll = form.save()
                return JsonResponse({
                    'success': True,
                    'id': str(payroll.id),
                    'message': f'Payroll record for {payroll.employee.get_full_name()} saved successfully!'
                })
            else:
                return super().form_valid(form)
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['An error occurred while saving the payroll record.']}
                }, status=500)
            else:
                raise e

    def form_invalid(self, form):
        # Check if this is an AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        else:
            return super().form_invalid(form)

class PayrollUpdateView(LoginRequiredMixin, UpdateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'human_resources/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def form_valid(self, form):
        try:
            # Check if this is an AJAX request
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                payroll = form.save()
                return JsonResponse({
                    'success': True,
                    'id': str(payroll.id),
                    'message': f'Payroll record for {payroll.employee.get_full_name()} updated successfully!'
                })
            else:
                return super().form_valid(form)
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['An error occurred while updating the payroll record.']}
                }, status=500)
            else:
                raise e

    def form_invalid(self, form):
        # Check if this is an AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        else:
            return super().form_invalid(form)

class PayrollDetailView(LoginRequiredMixin, DetailView):
    model = Payroll
    template_name = 'human_resources/payroll_detail.html'

class PayrollDeleteView(LoginRequiredMixin, DeleteView):
    model = Payroll
    template_name = 'human_resources/payroll_confirm_delete.html'
    success_url = reverse_lazy('hr:payroll_list')

# Training Views
class TrainingListView(LoginRequiredMixin, ListView):
    model = Training
    template_name = 'human_resources/training_list.html'
    context_object_name = 'trainings'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee')
        # Filter by employee if requested
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        return queryset.order_by('-date_completed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics
        context['total_trainings'] = Training.objects.count()
        context['recent_trainings'] = Training.objects.select_related('employee')[:5]
        return context

class TrainingCreateView(LoginRequiredMixin, CreateView):
    model = Training
    form_class = TrainingForm
    template_name = 'human_resources/training_form.html'
    success_url = reverse_lazy('hr:training_list')

    def form_valid(self, form):
        messages.success(self.request, f'Training record for {form.instance.employee.get_full_name()} created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('hr:training_list')

class TrainingUpdateView(LoginRequiredMixin, UpdateView):
    model = Training
    form_class = TrainingForm
    template_name = 'human_resources/training_form.html'
    success_url = reverse_lazy('hr:training_list')

    def form_valid(self, form):
        messages.success(self.request, f'Training record for {form.instance.employee.get_full_name()} updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('hr:training_list')

class TrainingDetailView(LoginRequiredMixin, DetailView):
    model = Training
    template_name = 'human_resources/training_detail.html'
    context_object_name = 'training'

class TrainingDeleteView(LoginRequiredMixin, DeleteView):
    model = Training
    template_name = 'human_resources/training_confirm_delete.html'
    success_url = reverse_lazy('hr:training_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_name'] = self.object.employee.get_full_name()
        return context

    def delete(self, request, *args, **kwargs):
        training = self.get_object()
        employee_name = training.employee.get_full_name()
        messages.success(request, f'Training record "{training.training_name}" for {employee_name} deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ExportMixin:
    def get_filename(self, request, model_name, format_type):
        return f"{model_name}_{request.GET.get('filter', '')}_{self.get_timestamp()}.{format_type}"

    def get_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime("%Y%m%d_%H%M%S")

class TrainingExportView(LoginRequiredMixin, ExportMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            format_type = request.GET.get('format', 'csv')
            queryset = self.get_queryset()

            if format_type == 'csv':
                return self.export_csv(queryset)
            elif format_type == 'excel':
                return self.export_excel(queryset)
            else:
                return HttpResponse("Invalid export format", status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Training export error: {str(e)}")
            return HttpResponse(f"Export failed: {str(e)}", status=500)

    def get_queryset(self):
        queryset = Training.objects.select_related('employee')
        employee_id = self.request.GET.get('employee')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if date_from:
            queryset = queryset.filter(date_completed__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_completed__lte=date_to)

        return queryset.order_by('-date_completed')

    def export_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "training", "csv")}"'

        writer = csv.writer(response)
        # Write headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Training Name', 'Description',
            'Date Completed', 'Certification Status', 'Provider', 'Duration (hours)',
            'Cost', 'Certificate Number', 'Expiry Date', 'Created At', 'Updated At'
        ])

        # Write data
        for record in queryset:
            writer.writerow([
                str(record.employee.id),
                record.employee.get_full_name(),
                record.training_name,
                record.description or '',
                record.date_completed,
                record.certification_status or '',
                record.provider or '',
                record.duration_hours,
                record.cost,
                record.certificate_number or '',
                record.expiry_date,
                record.created_at,
                record.updated_at
            ])

        return response

    def export_excel(self, queryset):
        from django.utils import timezone

        # Create a DataFrame
        data = []
        for record in queryset:
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            created_at = record.created_at
            updated_at = record.updated_at

            if created_at and timezone.is_aware(created_at):
                created_at = timezone.localtime(created_at).replace(tzinfo=None)
            if updated_at and timezone.is_aware(updated_at):
                updated_at = timezone.localtime(updated_at).replace(tzinfo=None)

            data.append({
                'Employee ID': str(record.employee.id),
                'Employee Name': record.employee.get_full_name(),
                'Training Name': record.training_name,
                'Training Type': record.training_type,
                'Date Completed': record.date_completed,
                'Duration (hours)': record.duration_hours,
                'Trainer': record.trainer or '',
                'Cost': float(record.cost) if record.cost else 0,
                'Certification': 'Yes' if record.certification_earned else 'No',
                'Notes': record.notes or '',
                'Created At': created_at,
                'Updated At': updated_at
            })

        df = pd.DataFrame(data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Training')

            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Training']

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "training", "xlsx")}"'

        return response

class AttendanceExportView(LoginRequiredMixin, ExportMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            format_type = request.GET.get('format', 'csv')
            queryset = self.get_queryset()

            if format_type == 'csv':
                return self.export_csv(request, queryset)
            elif format_type == 'excel':
                return self.export_excel(request, queryset)
            else:
                return HttpResponse("Invalid export format", status=400)
        except Exception as e:
            # Log the error and return a user-friendly response
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Attendance export error: {str(e)}")

            # Return a simple error response
            return HttpResponse(f"Export failed: {str(e)}", status=500)
    
    def get_queryset(self):
        queryset = Attendance.objects.all()
        employee_id = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        return queryset.order_by('-date')
    
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(request, "attendance", "csv")}"'

        writer = csv.writer(response)
        # Write headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Date', 'Clock In', 'Clock Out',
            'Status', 'Hours Worked', 'Total Hours', 'Overtime Hours', 'Location',
            'Shift Type', 'Clock Method', 'Approval Status', 'Approved By',
            'Notes', 'Supervisor Notes', 'Created At', 'Updated At'
        ])

        # Write data
        for record in queryset:
            writer.writerow([
                str(record.employee.id),
                record.employee.get_full_name(),
                record.date,
                record.clock_in,
                record.clock_out,
                record.get_status_display(),
                record.regular_hours_worked,
                record.total_hours_worked,
                record.overtime_hours,
                record.location,
                record.get_shift_type_display(),
                record.get_clock_method_display(),
                record.get_approval_status_display(),
                record.approved_by.get_full_name() if record.approved_by else '',
                record.notes,
                record.supervisor_notes,
                record.created_at,
                record.updated_at
            ])

        return response
    
    def export_excel(self, queryset):
        from django.utils import timezone

        # Create a DataFrame
        data = []
        for record in queryset:
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            created_at = record.created_at
            updated_at = record.updated_at

            if created_at and timezone.is_aware(created_at):
                created_at = timezone.localtime(created_at).replace(tzinfo=None)
            if updated_at and timezone.is_aware(updated_at):
                updated_at = timezone.localtime(updated_at).replace(tzinfo=None)

            data.append({
                'Employee ID': str(record.employee.id),
                'Employee Name': record.employee.get_full_name(),
                'Date': record.date,
                'Clock In': record.clock_in.strftime('%H:%M') if record.clock_in else '',
                'Clock Out': record.clock_out.strftime('%H:%M') if record.clock_out else '',
                'Status': record.get_status_display(),
                'Hours Worked': record.regular_hours_worked,
                'Total Hours': record.total_hours_worked,
                'Overtime Hours': record.overtime_hours,
                'Location': record.location,
                'Shift Type': record.get_shift_type_display(),
                'Clock Method': record.get_clock_method_display(),
                'Approval Status': record.get_approval_status_display(),
                'Approved By': record.approved_by.get_full_name() if record.approved_by else '',
                'Notes': record.notes or '',
                'Supervisor Notes': record.supervisor_notes or '',
                'Created At': created_at,
                'Updated At': updated_at
            })

        df = pd.DataFrame(data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance')

            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Attendance']

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "attendance", "xlsx")}"'

        return response

class PayrollExportView(LoginRequiredMixin, ExportMixin, View):
    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'csv')
        queryset = self.get_queryset()
        
        if format_type == 'csv':
            return self.export_csv(queryset)
        elif format_type == 'excel':
            return self.export_excel(queryset)
        else:
            return HttpResponse("Invalid export format", status=400)
    
    def get_queryset(self):
        queryset = Payroll.objects.all()
        employee_id = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        period_start = self.request.GET.get('period_start')
        period_end = self.request.GET.get('period_end')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if status:
            queryset = queryset.filter(status=status)
        if period_start:
            queryset = queryset.filter(pay_period_start__gte=period_start)
        if period_end:
            queryset = queryset.filter(pay_period_end__lte=period_end)
            
        return queryset.order_by('-pay_period_end')
    
    def export_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "payroll", "csv")}"'
        
        writer = csv.writer(response)
        # Write headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Pay Period Start', 'Pay Period End',
            'Base Salary', 'Overtime Pay', 'Bonus', 'Deductions', 'Net Pay',
            'Payment Date', 'Status', 'Created At', 'Updated At'
        ])
        
        # Write data
        for record in queryset:
            writer.writerow([
                str(record.employee.id),
                record.employee.get_full_name(),
                record.pay_period_start,
                record.pay_period_end,
                record.base_salary,
                record.overtime_pay,
                record.bonus,
                record.deductions,
                record.net_pay,
                record.payment_date,
                record.get_status_display(),
                record.created_at,
                record.updated_at
            ])
        
        return response
    
    def export_excel(self, queryset):
        from django.utils import timezone
        
        # Create a DataFrame
        data = []
        for record in queryset:
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            created_at = record.created_at
            updated_at = record.updated_at
            
            if created_at and timezone.is_aware(created_at):
                created_at = timezone.localtime(created_at).replace(tzinfo=None)
            if updated_at and timezone.is_aware(updated_at):
                updated_at = timezone.localtime(updated_at).replace(tzinfo=None)
            
            data.append({
                'Employee ID': str(record.employee.id),
                'Employee Name': record.employee.get_full_name(),
                'Pay Period Start': record.pay_period_start,
                'Pay Period End': record.pay_period_end,
                'Base Salary': float(record.base_salary) if record.base_salary else 0,
                'Overtime Pay': float(record.overtime_pay) if record.overtime_pay else 0,
                'Bonus': float(record.bonus) if record.bonus else 0,
                'Deductions': float(record.deductions) if record.deductions else 0,
                'Net Pay': float(record.net_pay) if record.net_pay else 0,
                'Payment Date': record.payment_date,
                'Status': record.get_status_display(),
                'Created At': created_at,
                'Updated At': updated_at
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Payroll')
            
            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Payroll']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "payroll", "xlsx")}"'
        
        return response

class EmployeeExportView(LoginRequiredMixin, ExportMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            format_type = request.GET.get('format', 'csv')
            queryset = self.get_queryset()
            
            if format_type == 'csv':
                return self.export_csv(queryset)
            elif format_type == 'excel':
                return self.export_excel(queryset)
            else:
                return HttpResponse("Invalid export format", status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Employee export error: {str(e)}")
            return HttpResponse(f"Export failed: {str(e)}", status=500)
    
    def get_queryset(self):
        queryset = Employee.objects.select_related('store', 'department', 'manager')
        
        # Apply filters
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(position__icontains=search)
            )
        
        store_id = self.request.GET.get('store')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        return queryset.order_by('last_name', 'first_name')
    
    def export_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "employees", "csv")}"'
        
        writer = csv.writer(response)
        # Write headers
        writer.writerow([
            'Employee ID', 'First Name', 'Last Name', 'Email', 'Username', 'Phone',
            'Position', 'Hire Date', 'Salary', 'Store', 'Department', 'Manager',
            'Active', 'Created At', 'Updated At'
        ])
        
        # Write data
        for employee in queryset:
            writer.writerow([
                str(employee.id),
                employee.first_name,
                employee.last_name,
                employee.email,
                employee.username,
                employee.phone or '',
                employee.position or '',
                employee.hire_date or '',
                employee.salary or '',
                employee.store.store_name if employee.store else '',
                employee.department.department_name if employee.department else '',
                employee.manager.get_full_name() if employee.manager else '',
                'Yes' if employee.is_active else 'No',
                employee.created_at,
                employee.updated_at
            ])
        
        return response
    
    def export_excel(self, queryset):
        from django.utils import timezone
        
        # Create a DataFrame
        data = []
        for employee in queryset:
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            created_at = employee.created_at
            updated_at = employee.updated_at
            
            if created_at and timezone.is_aware(created_at):
                created_at = timezone.localtime(created_at).replace(tzinfo=None)
            if updated_at and timezone.is_aware(updated_at):
                updated_at = timezone.localtime(updated_at).replace(tzinfo=None)
            
            data.append({
                'Employee ID': str(employee.id),
                'First Name': employee.first_name,
                'Last Name': employee.last_name,
                'Email': employee.email,
                'Username': employee.username,
                'Phone': employee.phone or '',
                'Position': employee.position or '',
                'Hire Date': employee.hire_date,
                'Salary': float(employee.salary) if employee.salary else 0,
                'Store': employee.store.store_name if employee.store else '',
                'Department': employee.department.department_name if employee.department else '',
                'Manager': employee.manager.get_full_name() if employee.manager else '',
                'Active': 'Yes' if employee.is_active else 'No',
                'Created At': created_at,
                'Updated At': updated_at
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')
            
            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Employees']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "employees", "xlsx")}"'
        
        return response

# Shift Views
class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = 'human_resources/shift_list.html'
    context_object_name = 'shifts'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by shift type
        shift_type = self.request.GET.get('shift_type')
        if shift_type:
            queryset = queryset.filter(shift_type=shift_type)

        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics
        context['total_shifts'] = Shift.objects.count()
        context['active_shifts'] = Shift.objects.filter(is_active=True).count()
        context['inactive_shifts'] = Shift.objects.filter(is_active=False).count()
        return context

class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    fields = ['name', 'shift_type', 'start_time', 'end_time', 'description', 'is_active', 'allowed_stores', 'allowed_departments']
    template_name = 'human_resources/shift_form.html'
    success_url = reverse_lazy('hr:shift_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Import here to avoid circular imports
        from store_management.models import Store, Department
        context['stores'] = Store.objects.all()
        context['departments'] = Department.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Shift "{form.instance.name}" created successfully!')
        return super().form_valid(form)

class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = Shift
    fields = ['name', 'shift_type', 'start_time', 'end_time', 'description', 'is_active', 'allowed_stores', 'allowed_departments']
    template_name = 'human_resources/shift_form.html'
    success_url = reverse_lazy('hr:shift_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Import here to avoid circular imports
        from store_management.models import Store, Department
        context['stores'] = Store.objects.all()
        context['departments'] = Department.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Shift "{form.instance.name}" updated successfully!')
        return super().form_valid(form)

class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift
    template_name = 'human_resources/shift_detail.html'
    context_object_name = 'shift'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related schedules
        context['schedules'] = self.object.schedules.select_related('employee').order_by('-date')[:10]
        context['total_schedules'] = self.object.schedules.count()
        return context

class ShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = Shift
    template_name = 'human_resources/shift_confirm_delete.html'
    success_url = reverse_lazy('hr:shift_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related data counts
        context['schedule_count'] = self.object.schedules.count()
        return context

    def delete(self, request, *args, **kwargs):
        shift = self.get_object()
        messages.success(request, f'Shift "{shift.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Schedule Views
class ScheduleListView(LoginRequiredMixin, ListView):
    model = Schedule
    template_name = 'human_resources/schedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee', 'shift', 'assigned_by')
        # Filter by employee
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by shift
        shift_id = self.request.GET.get('shift')
        if shift_id:
            queryset = queryset.filter(shift_id=shift_id)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics
        context['total_schedules'] = Schedule.objects.count()
        context['scheduled_count'] = Schedule.objects.filter(status='scheduled').count()
        context['confirmed_count'] = Schedule.objects.filter(status='confirmed').count()
        context['completed_count'] = Schedule.objects.filter(status='completed').count()
        context['cancelled_count'] = Schedule.objects.filter(status='cancelled').count()
        return context

class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Schedule
    fields = ['employee', 'shift', 'date', 'status', 'custom_start_time', 'custom_end_time', 'notes']
    template_name = 'human_resources/schedule_form.html'
    success_url = reverse_lazy('hr:schedule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(is_active=True)
        context['shifts'] = Shift.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        # Set assigned_by to current user if they are an employee
        try:
            employee = Employee.objects.get(user=self.request.user)
            form.instance.assigned_by = employee
        except Employee.DoesNotExist:
            pass

        messages.success(self.request, f'Schedule for {form.instance.employee.get_full_name()} on {form.instance.date} created successfully!')
        return super().form_valid(form)

class ScheduleUpdateView(LoginRequiredMixin, UpdateView):
    model = Schedule
    fields = ['employee', 'shift', 'date', 'status', 'custom_start_time', 'custom_end_time', 'notes', 'actual_start_time', 'actual_end_time']
    template_name = 'human_resources/schedule_form.html'
    success_url = reverse_lazy('hr:schedule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(is_active=True)
        context['shifts'] = Shift.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Schedule for {form.instance.employee.get_full_name()} on {form.instance.date} updated successfully!')
        return super().form_valid(form)

class ScheduleDetailView(LoginRequiredMixin, DetailView):
    model = Schedule
    template_name = 'human_resources/schedule_detail.html'
    context_object_name = 'schedule'

class ScheduleDeleteView(LoginRequiredMixin, DeleteView):
    model = Schedule
    template_name = 'human_resources/schedule_confirm_delete.html'
    success_url = reverse_lazy('hr:schedule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_name'] = self.object.employee.get_full_name()
        return context

    def delete(self, request, *args, **kwargs):
        schedule = self.get_object()
        employee_name = schedule.employee.get_full_name()
        date = schedule.date
        messages.success(request, f'Schedule for {employee_name} on {date} deleted successfully!')
        return super().delete(request, *args, **kwargs)

def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            return JsonResponse({'success': True, 'id': attendance.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = AttendanceForm()
    return render(request, 'human_resources/attendance_form.html', {'form': form})


# Leave Application Views
class LeaveApplicationListView(LoginRequiredMixin, ListView):
    model = LeaveApplication
    template_name = 'human_resources/leave_application_list.html'
    context_object_name = 'leave_applications'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee')
        # Filter by employee if requested
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by leave type
        leave_type = self.request.GET.get('leave_type')
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics
        context['total_applications'] = LeaveApplication.objects.count()
        context['pending_applications'] = LeaveApplication.objects.filter(status='pending').count()
        context['approved_applications'] = LeaveApplication.objects.filter(status='approved').count()
        context['rejected_applications'] = LeaveApplication.objects.filter(status='rejected').count()
        return context


class LeaveApplicationCreateView(LoginRequiredMixin, CreateView):
    model = LeaveApplication
    form_class = LeaveApplicationForm
    template_name = 'human_resources/leave_application_form.html'
    success_url = reverse_lazy('hr:leave_application_list')

    def form_valid(self, form):
        messages.success(self.request, f'Leave application for {form.instance.employee.get_full_name()} created successfully!')
        return super().form_valid(form)


class LeaveApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = LeaveApplication
    form_class = LeaveApplicationForm
    template_name = 'human_resources/leave_application_form.html'
    success_url = reverse_lazy('hr:leave_application_list')

    def form_valid(self, form):
        messages.success(self.request, f'Leave application for {form.instance.employee.get_full_name()} updated successfully!')
        return super().form_valid(form)


class LeaveApplicationDetailView(LoginRequiredMixin, DetailView):
    model = LeaveApplication
    template_name = 'human_resources/leave_application_detail.html'
    context_object_name = 'leave_application'


class LeaveApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = LeaveApplication
    template_name = 'human_resources/leave_application_confirm_delete.html'
    success_url = reverse_lazy('hr:leave_application_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_name'] = self.object.employee.get_full_name()
        return context

    def delete(self, request, *args, **kwargs):
        leave_app = self.get_object()
        employee_name = leave_app.employee.get_full_name()
        messages.success(request, f'Leave application for {employee_name} deleted successfully!')
        return super().delete(request, *args, **kwargs)


class LeaveApplicationExportView(LoginRequiredMixin, ExportMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            format_type = request.GET.get('format', 'csv')
            queryset = self.get_queryset()

            if format_type == 'csv':
                return self.export_csv(queryset)
            elif format_type == 'excel':
                return self.export_excel(queryset)
            else:
                return HttpResponse("Invalid export format", status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Leave application export error: {str(e)}")
            return HttpResponse(f"Export failed: {str(e)}", status=500)

    def get_queryset(self):
        queryset = LeaveApplication.objects.select_related('employee')
        employee_id = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        leave_type = self.request.GET.get('leave_type')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if status:
            queryset = queryset.filter(status=status)
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(end_date__lte=date_to)

        return queryset.order_by('-created_at')

    def export_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "leave_applications", "csv")}"'

        writer = csv.writer(response)
        # Write headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Leave Type', 'Start Date', 'End Date',
            'Reason', 'Status', 'Created At', 'Updated At'
        ])

        # Write data
        for record in queryset:
            writer.writerow([
                str(record.employee.id),
                record.employee.get_full_name(),
                record.get_leave_type_display(),
                record.start_date,
                record.end_date,
                record.reason or '',
                record.get_status_display(),
                record.created_at,
                record.updated_at
            ])

        return response

    def export_excel(self, queryset):
        from django.utils import timezone

        # Create a DataFrame
        data = []
        for record in queryset:
            # Convert timezone-aware datetimes to timezone-naive for Excel compatibility
            created_at = record.created_at
            updated_at = record.updated_at

            if created_at and timezone.is_aware(created_at):
                created_at = timezone.localtime(created_at).replace(tzinfo=None)
            if updated_at and timezone.is_aware(updated_at):
                updated_at = timezone.localtime(updated_at).replace(tzinfo=None)

            data.append({
                'Employee ID': str(record.employee.id),
                'Employee Name': record.employee.get_full_name(),
                'Leave Type': record.get_leave_type_display(),
                'Start Date': record.start_date,
                'End Date': record.end_date,
                'Reason': record.reason or '',
                'Status': record.get_status_display(),
                'Created At': created_at,
                'Updated At': updated_at
            })

        df = pd.DataFrame(data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Leave Applications')

            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Leave Applications']

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename(self.request, "leave_applications", "xlsx")}"'

        return response
