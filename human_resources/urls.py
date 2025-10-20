# human_resources/urls.py
from django.urls import path
from . import views
from .views import AttendanceExportView, PayrollExportView, TrainingExportView, LeaveApplicationExportView

app_name = 'hr'

urlpatterns = [
    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<uuid:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<uuid:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),

    # Attendance URLs
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/<uuid:pk>/', views.AttendanceDetailView.as_view(), name='attendance_detail'),
    path('attendance/<uuid:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    path('attendance/<uuid:pk>/delete/', views.AttendanceDeleteView.as_view(), name='attendance_delete'),

    # Payroll URLs
    path('payroll/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payroll/create/', views.PayrollCreateView.as_view(), name='payroll_create'),
    path('payroll/<uuid:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
    path('payroll/<uuid:pk>/edit/', views.PayrollUpdateView.as_view(), name='payroll_update'),
    path('payroll/<uuid:pk>/delete/', views.PayrollDeleteView.as_view(), name='payroll_delete'),

    # Training URLs
    path('training/', views.TrainingListView.as_view(), name='training_list'),
    path('training/create/', views.TrainingCreateView.as_view(), name='training_create'),
    path('training/<uuid:pk>/', views.TrainingDetailView.as_view(), name='training_detail'),
    path('training/<uuid:pk>/edit/', views.TrainingUpdateView.as_view(), name='training_update'),
    path('training/<uuid:pk>/delete/', views.TrainingDeleteView.as_view(), name='training_delete'),

    # Leave Application URLs
    path('leave-applications/', views.LeaveApplicationListView.as_view(), name='leave_application_list'),
    path('leave-applications/create/', views.LeaveApplicationCreateView.as_view(), name='leave_application_create'),
    path('leave-applications/<uuid:pk>/', views.LeaveApplicationDetailView.as_view(), name='leave_application_detail'),
    path('leave-applications/<uuid:pk>/edit/', views.LeaveApplicationUpdateView.as_view(), name='leave_application_update'),
    path('leave-applications/<uuid:pk>/delete/', views.LeaveApplicationDeleteView.as_view(), name='leave_application_delete'),

    # Shift URLs
    path('shifts/', views.ShiftListView.as_view(), name='shift_list'),
    path('shifts/create/', views.ShiftCreateView.as_view(), name='shift_create'),
    path('shifts/<uuid:pk>/', views.ShiftDetailView.as_view(), name='shift_detail'),
    path('shifts/<uuid:pk>/edit/', views.ShiftUpdateView.as_view(), name='shift_update'),
    path('shifts/<uuid:pk>/delete/', views.ShiftDeleteView.as_view(), name='shift_delete'),

    # Schedule URLs
    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/<uuid:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedules/<uuid:pk>/edit/', views.ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedules/<uuid:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),

    # Export URLs
    path('employees/export/', views.EmployeeExportView.as_view(), name='employee_export'),
    path('attendance/export/', AttendanceExportView.as_view(), name='attendance_export'),
    path('payroll/export/', PayrollExportView.as_view(), name='payroll_export'),
    path('training/export/', TrainingExportView.as_view(), name='training_export'),
    path('leave-applications/export/', LeaveApplicationExportView.as_view(), name='leave_application_export'),
]
