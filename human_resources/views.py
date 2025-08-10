# from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Attendance, Payroll
from .forms import AttendanceForm, PayrollForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from django.http import HttpResponse
from django.views import View
import csv
import pandas as pd
from io import BytesIO

# human_resources/views.py


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
        # Note: removed created_by since it's not in the model
        return super().form_valid(form)

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
        format_type = request.GET.get('format', 'csv')
        queryset = self.get_queryset()
        
        if format_type == 'csv':
            return self.export_csv(queryset)
        elif format_type == 'excel':
            return self.export_excel(queryset)
        else:
            return HttpResponse("Invalid export format", status=400)
    
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
        # Create a DataFrame
        data = []
        for record in queryset:
            data.append({
                'Employee ID': record.employee.employee_id,
                'Employee Name': record.employee.get_full_name(),
                'Date': record.date,
                'Clock In': record.clock_in,
                'Clock Out': record.clock_out,
                'Status': record.get_status_display(),
                'Notes': record.notes,
                'Created At': record.created_at,
                'Updated At': record.updated_at
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance')
        
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
        # Create a DataFrame
        data = []
        for record in queryset:
            data.append({
                'Employee ID': record.employee.employee_id,
                'Employee Name': record.employee.get_full_name(),
                'Pay Period Start': record.pay_period_start,
                'Pay Period End': record.pay_period_end,
                'Base Salary': record.base_salary,
                'Overtime Pay': record.overtime_pay,
                'Bonus': record.bonus,
                'Deductions': record.deductions,
                'Net Pay': record.net_pay,
                'Payment Date': record.payment_date,
                'Status': record.get_status_display(),
                'Created At': record.created_at,
                'Updated At': record.updated_at
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Payroll')
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.get_filename("payroll", "xlsx")}"'
        
        return response
