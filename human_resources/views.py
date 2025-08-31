# from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from .models import Attendance, Payroll, Employee
from .forms import AttendanceForm, PayrollForm
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
    template_name = 'human_resources/employee_form.html'
    fields = [
        'first_name', 'last_name', 'email', 'username', 'phone',
        'hire_date', 'position', 'salary', 'store', 'department', 'manager'
    ]
    
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
    template_name = 'human_resources/employee_form.html'
    fields = [
        'first_name', 'last_name', 'email', 'phone',
        'hire_date', 'position', 'salary', 'store', 'department', 'manager', 'is_active'
    ]
    
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

class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'human_resources/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                messages.error(
                    self.request,
                    'Attendance record already exists for this employee on the selected date. '
                    'Please update the existing record instead.'
                )
                return self.form_invalid(form)
            else:
                raise e

class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'human_resources/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

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



class ExportMixin:
    def get_filename(self, model_name, format_type):
        return f"{model_name}_{self.request.GET.get('filter', '')}_{self.get_timestamp()}.{format_type}"

    def get_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime("%Y%m%d_%H%M%S")

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
                record.employee.employee_id,
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
                'Employee ID': record.employee.employee_id,
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
                record.employee.employee_id,
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
                'Employee ID': record.employee.employee_id,
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
                employee.employee_id,
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
                'Employee ID': employee.employee_id,
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
