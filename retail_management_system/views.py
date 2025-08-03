from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from django.utils import timezone
from django.db.models import Sum
from datetime import date

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add dashboard statistics
        try:
            from store_management.models import Store
            context['store_count'] = Store.objects.count()
        except:
            context['store_count'] = 0
            
        try:
            from human_resources.models import Employee
            context['employee_count'] = Employee.objects.filter(is_active=True).count()
        except:
            context['employee_count'] = 0
            
        try:
            from inventory.models import Product
            context['inventory_count'] = Product.objects.count()
        except:
            context['inventory_count'] = 0
            
        try:
            from procurement.models import Supplier
            context['supplier_count'] = Supplier.objects.count()
        except:
            context['supplier_count'] = 0
            
        # Sales statistics
        try:
            from sales.models import Sale, Customer
            context['sales_count'] = Sale.objects.count()
            context['customer_count'] = Customer.objects.count()
            
            # Today's revenue
            today = date.today()
            today_sales = Sale.objects.filter(sale_date__date=today)
            context['today_revenue'] = today_sales.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
        except:
            context['sales_count'] = 0
            context['customer_count'] = 0
            context['today_revenue'] = 0
            
        # E-commerce statistics
        try:
            from e_commerce.models import OnlineOrder
            context['online_orders_count'] = OnlineOrder.objects.count()
        except:
            context['online_orders_count'] = 0
        
        return context


class CustomLogoutView(View):
    """Custom logout view that handles both GET and POST requests"""
    
    def get(self, request):
        logout(request)
        return redirect('/accounts/login/')
    
    def post(self, request):
        logout(request)
        return redirect('/accounts/login/')