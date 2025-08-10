# human_resources/urls.py
from django.urls import path
from . import views
from .views import AttendanceExportView, PayrollExportView

app_name = 'hr'

urlpatterns = [
    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    # Attendance URLs
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance_detail'),
    path('attendance/<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    path('attendance/<int:pk>/delete/', views.AttendanceDeleteView.as_view(), name='attendance_delete'),
    
    # Payroll URLs
    path('payroll/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payroll/create/', views.PayrollCreateView.as_view(), name='payroll_create'),
    path('payroll/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
    path('payroll/<int:pk>/edit/', views.PayrollUpdateView.as_view(), name='payroll_update'),
    path('payroll/<int:pk>/delete/', views.PayrollDeleteView.as_view(), name='payroll_delete'),

    # Export URLs
    path('employees/export/', views.EmployeeExportView.as_view(), name='employee_export'),
    path('attendance/export/', AttendanceExportView.as_view(), name='attendance_export'),
    path('payroll/export/', PayrollExportView.as_view(), name='payroll_export'),
]