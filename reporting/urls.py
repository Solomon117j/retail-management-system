# reporting/urls.py
from django.urls import path
from . import views

app_name = 'analytics'  # Using 'analytics' as the namespace to match the template

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('sales/', views.SalesReportView.as_view(), name='sales_report'),
    path('inventory/', views.InventoryReportView.as_view(), name='inventory_report'),
    path('employees/', views.EmployeeReportView.as_view(), name='employee_report'),
]