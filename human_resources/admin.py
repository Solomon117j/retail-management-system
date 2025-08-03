from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Payroll, Attendance

# Register your models here.

@admin.register(Employee)  # <-- This decorator registers the model
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'department', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('department',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('department',)}),
    )
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'clock_in', 'clock_out')
    list_filter = ('status', 'date')
    search_fields = ('employee__user__username', 'notes')

    def export_reports(self, obj):
        url = reverse('hr:attendance_export')
        return format_html('<a class="button" href="{}">Export CSV</a>&nbsp;<a class="button" href="{}?format=excel">Export Excel</a>',
                           url, url)
    
    export_reports.short_description = 'Export Reports'
    export_reports.allow_tags = True


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'pay_period_start', 'pay_period_end', 'net_pay', 'status')
    list_filter = ('status', 'pay_period_end')
    search_fields = ('employee__user__username',)

    def export_reports(self, obj):
        url = reverse('hr:payroll_export')
        return format_html('<a class="button" href="{}">Export CSV</a>&nbsp;<a class="button" href="{}?format=excel">Export Excel</a>',
                           url, url)
    
    export_reports.short_description = 'Export Reports'
    export_reports.allow_tags = True
