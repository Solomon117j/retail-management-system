from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Customer, Sale, SaleItem, Return, LoyaltyTransaction
from store_management.models import Store
from human_resources.models import Employee
from inventory.models import Product
import datetime

# ====================
# CUSTOMER VIEWS
# ====================

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        membership = self.request.GET.get('membership')
        
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        if membership:
            queryset = queryset.filter(membership_level=membership)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['membership_levels'] = Customer.MEMBERSHIP_CHOICES
        return context

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = 'sales/customer_form.html'
    fields = [
        'first_name', 'last_name', 'email', 'phone', 
        'address', 'city', 'postal_code', 'join_date',
        'membership_level'
    ]
    success_url = reverse_lazy('customer_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Customer "{self.object}" created successfully')
        return response

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = 'sales/customer_form.html'
    fields = [
        'first_name', 'last_name', 'email', 'phone', 
        'address', 'city', 'postal_code', 'join_date',
        'membership_level'
    ]
    
    def get_success_url(self):
        return reverse('customer_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Customer "{self.object}" updated successfully')
        return response

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'sales/customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchases'] = self.object.purchases.all().order_by('-sale_date')[:10]
        context['transactions'] = self.object.loyalty_transactions.all().order_by('-transaction_date')[:10]
        return context

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'sales/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')
    
    def delete(self, request, *args, **kwargs):
        customer = self.get_object()
        messages.success(request, f'Customer "{customer}" deleted successfully')
        return super().delete(request, *args, **kwargs)

# ====================
# SALE VIEWS
# ====================

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'store', 'employee', 'customer'
        ).prefetch_related('items')
        
        # Date filtering
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            # Add 1 day to include end_date
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
            queryset = queryset.filter(sale_date__lte=end_date)
            
        return queryset.order_by('-sale_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stores'] = Store.objects.all()
        return context

class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    template_name = 'sales/sale_form.html'
    fields = [
        'store', 'employee', 'customer', 
        'sale_date', 'payment_method',
        'discount_amount', 'tax_amount'
    ]
    
    def get_initial(self):
        initial = super().get_initial()
        initial['sale_date'] = datetime.datetime.now()
        initial['employee'] = self.request.user.employee
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create formset for sale items
        SaleItemFormSet = inlineformset_factory(
            Sale, 
            SaleItem, 
            fields=('product', 'quantity', 'unit_price', 'discount_percentage'),
            extra=3,
            can_delete=True
        )
        
        if self.request.POST:
            context['formset'] = SaleItemFormSet(self.request.POST)
        else:
            context['formset'] = SaleItemFormSet()
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                
                # Recalculate total amount
                self.object.total_amount = sum(
                    item.quantity * item.unit_price * (1 - item.discount_percentage / 100)
                    for item in self.object.items.all()
                )
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Sale #{self.object.id} created successfully')
        return redirect('sale_detail', pk=self.object.pk)

class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    template_name = 'sales/sale_form.html'
    fields = [
        'store', 'employee', 'customer', 
        'sale_date', 'payment_method',
        'discount_amount', 'tax_amount'
    ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create formset for sale items
        SaleItemFormSet = inlineformset_factory(
            Sale, 
            SaleItem, 
            fields=('product', 'quantity', 'unit_price', 'discount_percentage'),
            extra=1,
            can_delete=True
        )
        
        if self.request.POST:
            context['formset'] = SaleItemFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['formset'] = SaleItemFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                
                # Recalculate total amount
                self.object.total_amount = sum(
                    item.quantity * item.unit_price * (1 - item.discount_percentage / 100)
                    for item in self.object.items.all()
                )
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Sale #{self.object.id} updated successfully')
        return redirect('sale_detail', pk=self.object.pk)

class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        context['returns'] = self.object.returns.all()
        context['loyalty_transactions'] = self.object.loyalty_transactions.all()
        return context

class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sale_list')
    
    def delete(self, request, *args, **kwargs):
        sale = self.get_object()
        messages.success(request, f'Sale #{sale.id} deleted successfully')
        return super().delete(request, *args, **kwargs)

# ====================
# RETURN VIEWS
# ====================

class ReturnCreateView(LoginRequiredMixin, CreateView):
    model = Return
    template_name = 'sales/return_form.html'
    fields = [
        'sale', 'return_date', 'reason', 
        'refund_amount', 'refund_method', 'employee'
    ]
    
    def get_initial(self):
        initial = super().get_initial()
        sale_id = self.request.GET.get('sale_id')
        
        if sale_id:
            sale = get_object_or_404(Sale, pk=sale_id)
            initial['sale'] = sale
            initial['refund_amount'] = sale.total_amount
            initial['employee'] = self.request.user.employee
        
        initial['return_date'] = datetime.datetime.now()
        return initial
    
    def get_success_url(self):
        return reverse('sale_detail', kwargs={'pk': self.object.sale.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Return processed for Sale #{self.object.sale_id}')
        return response

class ReturnUpdateView(LoginRequiredMixin, UpdateView):
    model = Return
    template_name = 'sales/return_form.html'
    fields = [
        'return_date', 'reason', 
        'refund_amount', 'refund_method', 'employee'
    ]
    
    def get_success_url(self):
        return reverse('sale_detail', kwargs={'pk': self.object.sale.pk})

class ReturnDeleteView(LoginRequiredMixin, DeleteView):
    model = Return
    template_name = 'sales/return_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('sale_detail', kwargs={'pk': self.object.sale.pk})
    
    def delete(self, request, *args, **kwargs):
        return_obj = self.get_object()
        sale_id = return_obj.sale_id
        messages.success(request, 'Return deleted successfully')
        return super().delete(request, *args, **kwargs)

# ====================
# LOYALTY TRANSACTION VIEWS
# ====================

class LoyaltyTransactionCreateView(LoginRequiredMixin, CreateView):
    model = LoyaltyTransaction
    template_name = 'sales/loyaltytransaction_form.html'
    fields = ['customer', 'sale', 'points_earned', 'points_redeemed', 'transaction_date']
    
    def get_initial(self):
        initial = super().get_initial()
        customer_id = self.request.GET.get('customer_id')
        sale_id = self.request.GET.get('sale_id')
        
        if customer_id:
            initial['customer'] = get_object_or_404(Customer, pk=customer_id)
        if sale_id:
            initial['sale'] = get_object_or_404(Sale, pk=sale_id)
        
        initial['transaction_date'] = datetime.datetime.now()
        return initial
    
    def get_success_url(self):
        if self.object.customer:
            return reverse('customer_detail', kwargs={'pk': self.object.customer.pk})
        return reverse('sale_detail', kwargs={'pk': self.object.sale.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Loyalty transaction recorded')
        return response

class LoyaltyTransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = LoyaltyTransaction
    template_name = 'sales/loyaltytransaction_form.html'
    fields = ['points_earned', 'points_redeemed', 'transaction_date']
    
    def get_success_url(self):
        if self.object.customer:
            return reverse('customer_detail', kwargs={'pk': self.object.customer.pk})
        return reverse('sale_detail', kwargs={'pk': self.object.sale.pk})

class LoyaltyTransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = LoyaltyTransaction
    template_name = 'sales/loyaltytransaction_confirm_delete.html'
    
    def get_success_url(self):
        if self.object.customer:
            return reverse('customer_detail', kwargs={'pk': self.object.customer.pk})
        return reverse('sale_detail', kwargs={'pk': self.object.sale.pk})
    
    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        customer = transaction.customer
        
        # Reverse points before deletion
        customer.loyalty_points -= (transaction.points_earned - transaction.points_redeemed)
        customer.save()
        
        messages.success(request, 'Loyalty transaction deleted')
        return super().delete(request, *args, **kwargs)