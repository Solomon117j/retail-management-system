# core/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from store_management.models import Store
from human_resources.models import Employee
from inventory.models import Product
from procurement.models import Supplier
from sales.models import Sale, Customer
from e_commerce.models import OnlineOrder

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get stats from different apps
        context['store_count'] = Store.objects.count()
        context['employee_count'] = Employee.objects.filter(is_active=True).count()
        context['inventory_count'] = Product.objects.count()
        context['supplier_count'] = Supplier.objects.filter(is_active=True).count()
        context['sales_count'] = Sale.objects.count()
        context['customer_count'] = Customer.objects.count()
        context['online_orders_count'] = OnlineOrder.objects.count()
        
        return context