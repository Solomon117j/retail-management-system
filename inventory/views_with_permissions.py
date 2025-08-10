"""
Example of how to use the permission system in your views.
This shows how to integrate the permission decorators and mixins.
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Product
from .forms import ProductForm

# Import the permission utilities
from human_resources.permissions import (
    PermissionMixin, 
    require_permission, 
    require_any_permission,
    has_permission
)


# Example 1: Using PermissionMixin with class-based views
class ProductListView(PermissionMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    # Require either view_inventory or access_inventory permission
    required_permissions = ['view_inventory', 'access_inventory']
    permission_required_all = False  # User needs ANY of the permissions
    permission_denied_message = "You don't have permission to view the inventory."
    permission_denied_url = 'dashboards:dashboard'


class ProductDetailView(PermissionMixin, LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    
    # Require view_inventory permission
    required_permission = 'view_inventory'
    permission_denied_message = "You don't have permission to view product details."


class ProductCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    # Require edit_inventory permission to create products
    required_permission = 'edit_inventory'
    permission_denied_message = "You don't have permission to create products."
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    # Require edit_inventory permission to update products
    required_permission = 'edit_inventory'
    permission_denied_message = "You don't have permission to edit products."
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')
    
    # Require edit_inventory permission to delete products
    required_permission = 'edit_inventory'
    permission_denied_message = "You don't have permission to delete products."


# Example 2: Using decorators with function-based views
@require_permission('view_inventory', 
                   redirect_url='dashboards:dashboard',
                   message="You don't have permission to view the inventory dashboard.")
def inventory_dashboard(request):
    """Dashboard view for inventory management"""
    products = Product.objects.all()
    
    # Check if user can edit inventory to show edit buttons
    can_edit = has_permission(request.user, 'edit_inventory')
    
    context = {
        'products': products,
        'can_edit': can_edit,
        'total_products': products.count(),
    }
    return render(request, 'inventory/dashboard.html', context)


@require_any_permission('perform_inventory_audit', 'edit_inventory',
                       message="You don't have permission to perform inventory audits.")
def inventory_audit(request):
    """View for conducting inventory audits"""
    # Audit logic here
    return render(request, 'inventory/audit.html')


@require_permission('manage_inventory_categories')
def manage_categories(request):
    """View for managing inventory categories"""
    # Category management logic here
    return render(request, 'inventory/categories.html')


# Example 3: Custom permission checking in views
class AdvancedProductView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/advanced_product.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add permission-based context variables
        context.update({
            'can_view_inventory': has_permission(self.request.user, 'view_inventory'),
            'can_edit_inventory': has_permission(self.request.user, 'edit_inventory'),
            'can_audit_inventory': has_permission(self.request.user, 'perform_inventory_audit'),
            'can_manage_categories': has_permission(self.request.user, 'manage_inventory_categories'),
        })
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Custom permission logic
        if not has_permission(request.user, 'view_inventory'):
            messages.error(request, "You don't have permission to view product details.")
            return redirect('dashboards:dashboard')
        
        return super().dispatch(request, *args, **kwargs)