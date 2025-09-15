# from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from .models import Attendance, Payroll, Employee, Training, LeaveApplication
from .forms import AttendanceForm, PayrollForm, EmployeeForm, TrainingForm, LeaveApplicationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.contrib import messages
from django.shortcuts import get_object_or_404

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
import csv
import pandas as pd
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
        queryset = super().get_queryset()
        # Filter by employee if requested
        employee_id = self.request.GET.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
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
        # Note: removed created_by since it's not in the model
        return super().form_valid(form)

class PayrollUpdateView(LoginRequiredMixin, UpdateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'human_resources/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')

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
    def get_filename(self, model_name, format_type):
        return f"{model_name}_{self.request.GET.get('filter', '')}_{self.get_timestamp()}.{format_type}"

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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("training", "csv")}"'

        writer = csv.writer(response)
        # Write headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Training Name', 'Training Type',
            'Date Completed', 'Duration (hours)', 'Trainer', 'Cost',
            'Certification', 'Notes', 'Created At', 'Updated At'
        ])

        # Write data
        for record in queryset:
            writer.writerow([
                str(record.employee.id),
                record.employee.get_full_name(),
                record.training_name,
                record.training_type,
                record.date_completed,
                record.duration_hours,
                record.trainer or '',
                record.cost,
                'Yes' if record.certification_earned else 'No',
                record.notes or '',
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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("training", "xlsx")}"'

        return response

class AttendanceExportView(LoginRequiredMixin, ExportMixin, View):
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
    
    def export_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("attendance", "csv")}"'
        
        writer = csv.writer(response)
        # Write headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Date', 'Clock In', 'Clock Out',
            'Status', 'Notes', 'Created At', 'Updated At'
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
                record.notes,
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
                'Notes': record.notes or '',
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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("attendance", "xlsx")}"'
        
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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("payroll", "csv")}"'
        
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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("payroll", "xlsx")}"'
        
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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("employees", "csv")}"'
        
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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("employees", "xlsx")}"'
        
        return response

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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("leave_applications", "csv")}"'

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
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("leave_applications", "xlsx")}"'

        return response
