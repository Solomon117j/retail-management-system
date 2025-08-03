# ecommerce/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OnlineOrder, OrderItem
from sales.models import Customer
from store_management.models import Store
from inventory.models import Product

class OnlineOrderListView(LoginRequiredMixin, ListView):
    model = OnlineOrder
    template_name = 'ecommerce/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'customer', 'store_pickup'
        ).prefetch_related('items')
        
        status = self.request.GET.get('status')
        shipping_method = self.request.GET.get('shipping_method')
        
        if status:
            queryset = queryset.filter(status=status)
        if shipping_method:
            queryset = queryset.filter(shipping_method=shipping_method)
            
        return queryset.order_by('-order_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = OnlineOrder.STATUS_CHOICES
        context['shipping_choices'] = OnlineOrder.SHIPPING_METHOD_CHOICES
        return context

class OnlineOrderCreateView(LoginRequiredMixin, CreateView):
    model = OnlineOrder
    template_name = 'ecommerce/order_form.html'
    fields = [
        'customer', 'shipping_address', 'shipping_method',
        'payment_method', 'store_pickup', 'tracking_number'
    ]
    
    def get_initial(self):
        initial = super().get_initial()
        customer_id = self.request.GET.get('customer_id')
        
        if customer_id:
            customer = get_object_or_404(Customer, pk=customer_id)
            initial['customer'] = customer
            initial['shipping_address'] = customer.address
            
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create formset for order items
        OrderItemFormSet = inlineformset_factory(
            OnlineOrder, 
            OrderItem, 
            fields=('product', 'quantity', 'unit_price'),
            extra=3,
            can_delete=True
        )
        
        if self.request.POST:
            context['formset'] = OrderItemFormSet(self.request.POST)
        else:
            context['formset'] = OrderItemFormSet()
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save(commit=False)
            self.object.save()  # Save first to get ID for formset
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                
                # Recalculate total amount
                self.object.total_amount = sum(
                    item.quantity * item.unit_price 
                    for item in self.object.items.all()
                )
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Online Order #{self.object.id} created successfully')
        return redirect('ecommerce:order_detail', pk=self.object.pk)

class OnlineOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = OnlineOrder
    template_name = 'ecommerce/order_form.html'
    fields = [
        'shipping_address', 'shipping_method',
        'payment_method', 'store_pickup', 'tracking_number'
    ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create formset for order items
        OrderItemFormSet = inlineformset_factory(
            OnlineOrder, 
            OrderItem, 
            fields=('product', 'quantity', 'unit_price'),
            extra=1,
            can_delete=True
        )
        
        if self.request.POST:
            context['formset'] = OrderItemFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['formset'] = OrderItemFormSet(instance=self.object)
        
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
                    item.quantity * item.unit_price 
                    for item in self.object.items.all()
                )
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Online Order #{self.object.id} updated successfully')
        return redirect('ecommerce:order_detail', pk=self.object.pk)

class OnlineOrderDetailView(LoginRequiredMixin, DetailView):
    model = OnlineOrder
    template_name = 'ecommerce/order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        context['can_edit'] = self.object.status in ['pending', 'processing']
        return context

class OnlineOrderStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(OnlineOrder, pk=kwargs['pk'])
        new_status = request.POST.get('status')
        
        # State transition logic
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
        }
        
        if new_status in valid_transitions.get(order.status, []):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, f'Invalid status transition: {order.get_status_display()} to {new_status}')
        
        return redirect('ecommerce:order_detail', pk=order.pk)

class OnlineOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = OnlineOrder
    template_name = 'ecommerce/order_confirm_delete.html'
    success_url = reverse_lazy('ecommerce:order_list')
    
    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        messages.success(request, f'Online Order #{order.id} deleted successfully')
        return super().delete(request, *args, **kwargs)