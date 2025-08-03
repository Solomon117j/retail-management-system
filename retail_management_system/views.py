from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
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
            
        # Placeholder for pending tasks
        context['task_count'] = 0
        
        return context


class CustomLogoutView(View):
    """Custom logout view that handles both GET and POST requests"""
    
    def get(self, request):
        logout(request)
        return redirect('/accounts/login/')
    
    def post(self, request):
        logout(request)
        return redirect('/accounts/login/')