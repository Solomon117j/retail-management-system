# procurement/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.db import transaction, models
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Supplier, SupplierProduct, PurchaseOrder, PurchaseOrderItem
from .forms import SupplierForm, PurchaseOrderForm, PurchaseOrderItemForm, SupplierProductForm
from inventory.models import Product, StockMovement
from store_management.models import Store
from human_resources.models import Employee
import datetime

# ====================
# SUPPLIER VIEWS
# ====================

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'procurement/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Add search functionality
        if 'search' in self.request.GET:
            search_term = self.request.GET['search']
            return queryset.filter(name__icontains=search_term)
        return queryset

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'procurement/supplier_form.html'
    success_url = reverse_lazy('procurement:supplier_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'procurement/supplier_form.html'
    success_url = reverse_lazy('procurement:supplier_list')

class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'procurement/supplier_detail.html'
    context_object_name = 'supplier'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.supplier_products.all()
        context['orders'] = self.object.purchase_orders.all()
        return context

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'procurement/supplier_confirm_delete.html'
    success_url = reverse_lazy('procurement:supplier_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check for related objects that would prevent deletion
        context['purchase_orders'] = self.object.purchase_orders.all()
        context['supplier_products'] = self.object.supplier_products.all()
        context['can_delete'] = not (context['purchase_orders'].exists() or context['supplier_products'].exists())
        return context
    
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except models.ProtectedError as e:
            messages.error(
                request, 
                f"Cannot delete supplier '{self.get_object().name}' because it has related purchase orders or products. "
                "Please remove or reassign these items first."
            )
            return redirect('procurement:supplier_detail', pk=self.get_object().pk)

# ========================
# SUPPLIER PRODUCT VIEWS
# ========================

class SupplierProductCreateView(LoginRequiredMixin, CreateView):
    model = SupplierProduct
    form_class = SupplierProductForm
    template_name = 'procurement/supplierproduct_form.html'

    def get_initial(self):
        initial = super().get_initial()
        supplier = get_object_or_404(Supplier, pk=self.kwargs['supplier_id'])
        initial['supplier'] = supplier
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supplier'] = get_object_or_404(Supplier, pk=self.kwargs['supplier_id'])
        return context

    def form_valid(self, form):
        supplier = get_object_or_404(Supplier, pk=self.kwargs['supplier_id'])
        form.instance.supplier = supplier
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('procurement:supplier_detail', kwargs={'pk': self.kwargs['supplier_id']})

class SupplierProductUpdateView(LoginRequiredMixin, UpdateView):
    model = SupplierProduct
    form_class = SupplierProductForm
    template_name = 'procurement/supplierproduct_form.html'

    def get_success_url(self):
        return reverse('procurement:supplier_detail', kwargs={'pk': self.object.supplier.pk})

class SupplierProductDeleteView(LoginRequiredMixin, DeleteView):
    model = SupplierProduct
    template_name = 'procurement/supplierproduct_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('procurement:supplier_detail', kwargs={'pk': self.object.supplier.pk})

# ======================
# PURCHASE ORDER VIEWS
# ======================

class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'procurement/purchaseorder_list.html'
    context_object_name = 'orders'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('supplier', 'store')
        status = self.request.GET.get('status')
        supplier_id = self.request.GET.get('supplier')
        
        if status:
            queryset = queryset.filter(status=status)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
            
        return queryset.order_by('-order_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.all()
        context['status_choices'] = PurchaseOrder.ORDER_STATUS_CHOICES

        # Calculate status counts for summary cards from the filtered queryset
        from django.db.models import Count
        filtered_queryset = self.get_queryset()
        status_counts = filtered_queryset.aggregate(
            total_orders=Count('id'),
            pending_approval=Count('id', filter=models.Q(status='pending')),
            shipped=Count('id', filter=models.Q(status='shipped')),
            received=Count('id', filter=models.Q(status='received')),
        )
        context.update(status_counts)

        return context

class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'procurement/purchaseorder_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['can_edit'] = self.object.status in ['draft', 'pending']
        return context

class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'procurement/purchaseorder_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create formset for order items
        PurchaseOrderItemFormSet = inlineformset_factory(
            PurchaseOrder,
            PurchaseOrderItem,
            form=PurchaseOrderItemForm,
            extra=1,
            can_delete=True
        )

        if self.request.POST:
            context['formset'] = PurchaseOrderItemFormSet(self.request.POST)
        else:
            context['formset'] = PurchaseOrderItemFormSet()

        # Add products to context for empty form template
        from inventory.models import Product
        context['products'] = Product.objects.all().order_by('name')

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        form.instance.created_by = self.request.user.employee_profile.first()
        form.instance.status = 'draft'

        with transaction.atomic():
            self.object = form.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()

                # Recalculate total amount
                self.object.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('procurement:purchaseorder_list')

class PurchaseOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'procurement/purchaseorder_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create formset for order items
        PurchaseOrderItemFormSet = inlineformset_factory(
            PurchaseOrder,
            PurchaseOrderItem,
            form=PurchaseOrderItemForm,
            extra=1,
            can_delete=True
        )
        
        if self.request.POST:
            context['formset'] = PurchaseOrderItemFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['formset'] = PurchaseOrderItemFormSet(instance=self.object)

        # Add products to context for empty form template
        from inventory.models import Product
        context['products'] = Product.objects.all().order_by('name')
        
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
                self.object.save()
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('procurement:purchaseorder_detail', kwargs={'pk': self.object.pk})

class PurchaseOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = PurchaseOrder
    template_name = 'procurement/purchaseorder_confirm_delete.html'
    success_url = reverse_lazy('procurement:purchaseorder_list')

# =============================
# PURCHASE ORDER ACTION VIEWS
# =============================

class PurchaseOrderStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    fields = []
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        
        # State transition logic
        valid_transitions = {
            'draft': ['pending', 'cancelled'],
            'pending': ['approved', 'cancelled'],
            'approved': ['shipped'],
            'shipped': ['received', 'cancelled'],
        }
        
        if action in valid_transitions.get(self.object.status, []):
            self.object.status = action
            self.object.save()
            messages.success(request, f'Order status updated to {action}')
        else:
            messages.error(request, f'Invalid status transition: {self.object.status} to {action}')
        
        return redirect('procurement:purchaseorder_detail', pk=self.object.pk)

class PurchaseOrderReceiveView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    template_name = 'procurement/purchaseorder_receive.html'
    context_object_name = 'order'
    fields = []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.object.status != 'shipped':
            messages.error(request, 'Only shipped orders can be received')
            return redirect('procurement:purchaseorder_detail', pk=self.object.pk)
        
        # Process received quantities and update inventory via StockMovement
        for item in self.object.items.select_related('product').all():
            received_key = f'received_{item.id}'
            if received_key in request.POST:
                try:
                    received_qty = int(request.POST[received_key])
                    if 0 <= received_qty <= item.quantity:
                        # Calculate delta to apply to stock (new - previous)
                        delta = received_qty - (item.received_quantity or 0)
                        if delta != 0:
                            StockMovement.objects.create(
                                product=item.product,
                                store=self.object.store,
                                movement_type='IN',
                                quantity=abs(delta),
                                reference=f"PO-{self.object.id}",
                                created_by=request.user.employee_profile.first(),
                                reason='PURCHASE'
                            )
                            # Update received_quantity to new value
                            item.received_quantity = received_qty
                            item.save()
                    else:
                        messages.error(request, f'Invalid quantity for {item.product}')
                except ValueError:
                    messages.error(request, f'Invalid input for {item.product}')
        
        # Update order status if all items received
        if all(item.received_quantity == item.quantity for item in self.object.items.all()):
            self.object.status = 'received'
            self.object.save()
            messages.success(request, 'Order fully received and closed')
        else:
            messages.success(request, 'Partial receipt recorded')
        
        return redirect('procurement:purchaseorder_detail', pk=self.object.pk)