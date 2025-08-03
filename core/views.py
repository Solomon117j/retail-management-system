# core/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from store_management.models import Store, Employee
from inventory.models import Product

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get stats from different apps
        context['store_count'] = Store.objects.count()
        context['employee_count'] = Employee.objects.filter(is_active=True).count()
        context['inventory_count'] = Product.objects.count()
        
        # Example task count (customize based on your needs)
        context['task_count'] = 5  # Replace with actual task query
        
        return context