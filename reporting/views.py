from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from datetime import datetime, timedelta

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/analytics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get basic statistics
        try:
            from store_management.models import Store
            context['total_stores'] = Store.objects.count()
        except:
            context['total_stores'] = 0
            
        try:
            from human_resources.models import Employee
            context['total_employees'] = Employee.objects.filter(is_active=True).count()
        except:
            context['total_employees'] = 0
            
        try:
            from inventory.models import Product
            context['total_products'] = Product.objects.count()
            context['low_stock_products'] = Product.objects.filter(quantity_in_stock__lt=10).count()
        except:
            context['total_products'] = 0
            context['low_stock_products'] = 0
        
        # Add more analytics data here as needed
        context['current_month'] = datetime.now().strftime('%B %Y')
        
        return context

class SalesReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/sales_report.html'

class InventoryReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/inventory_report.html'

class EmployeeReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reporting/employee_report.html'
