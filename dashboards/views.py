# core/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from store_management.models import Store
from human_resources.models import Employee
from inventory.models import Product
from procurement.models import Supplier

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get stats from different apps
        context['store_count'] = Store.objects.count()
        context['employee_count'] = Employee.objects.filter(is_active=True).count()
        context['inventory_count'] = Product.objects.count()
        context['active_suppliers'] = Supplier.objects.filter(is_active=True)
        
        return context