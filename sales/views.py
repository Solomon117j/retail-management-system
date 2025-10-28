from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.db import transaction, models
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from .models import Customer, Sale, SaleItem, Return, LoyaltyTransaction, SalesTransaction
from .forms import (
    CustomerForm, SaleForm, SaleItemForm, ReturnForm,
    LoyaltyTransactionForm, SaleItemFormSet
)
from store_management.models import Store
from human_resources.models import Employee
from inventory.models import Product, InventoryRecord
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
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Customer "{self.object}" created successfully')
        return response

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    
    def get_success_url(self):
        return reverse('sales:customer_detail', kwargs={'pk': self.object.pk})
    
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
    success_url = reverse_lazy('sales:customer_list')
    
    def delete(self, request, *args, **kwargs):
        customer = self.get_object()
        messages.success(request, f'Customer "{customer}" deleted successfully')
        return super().delete(request, *args, **kwargs)

# ====================
# SALE VIEWS
# ====================

def validate_sale_stock(sale_items, store):
    """
    Validate that sufficient stock exists for all sale items at the given store.
    Raises ValidationError if insufficient stock.
    """
    insufficient_stock_items = []

    for item in sale_items:
        try:
            inventory_record = InventoryRecord.objects.get(
                product=item['product'],
                store=store
            )
            if inventory_record.quantity < item['quantity']:
                insufficient_stock_items.append({
                    'product': item['product'].name,
                    'requested': item['quantity'],
                    'available': inventory_record.quantity
                })
        except InventoryRecord.DoesNotExist:
            insufficient_stock_items.append({
                'product': item['product'].name,
                'requested': item['quantity'],
                'available': 0
            })

    if insufficient_stock_items:
        error_messages = []
        for item in insufficient_stock_items:
            error_messages.append(
                f"{item['product']}: requested {item['requested']}, available {item['available']}"
            )
        raise ValidationError(
            f"Insufficient stock for the following items: {', '.join(error_messages)}"
        )

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
        initial['employee'] = self.request.user
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

        # Validate stock before saving
        if formset.is_valid():
            sale_items = []
            for form_item in formset:
                if form_item.cleaned_data and not form_item.cleaned_data.get('DELETE', False):
                    sale_items.append({
                        'product': form_item.cleaned_data['product'],
                        'quantity': form_item.cleaned_data['quantity']
                    })

            try:
                validate_sale_stock(sale_items, form.cleaned_data['store'])
            except ValidationError as e:
                messages.error(self.request, str(e))
                return self.form_invalid(form)

        with transaction.atomic():
            form.instance.created_by = self.request.user.employee_profile
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

        # Validate stock before saving
        if formset.is_valid():
            sale_items = []
            for form_item in formset:
                if form_item.cleaned_data and not form_item.cleaned_data.get('DELETE', False):
                    sale_items.append({
                        'product': form_item.cleaned_data['product'],
                        'quantity': form_item.cleaned_data['quantity']
                    })

            try:
                validate_sale_stock(sale_items, form.cleaned_data['store'])
            except ValidationError as e:
                messages.error(self.request, str(e))
                return self.form_invalid(form)

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
    success_url = reverse_lazy('sales:sale_list')
    
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
            initial['employee'] = self.request.user
        
        initial['return_date'] = datetime.datetime.now()
        return initial
    
    def get_success_url(self):
        return reverse('sales:sale_detail', kwargs={'pk': self.object.sale.pk})
    
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
        return reverse('sales:sale_detail', kwargs={'pk': self.object.sale.pk})

class ReturnDeleteView(LoginRequiredMixin, DeleteView):
    model = Return
    template_name = 'sales/return_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('sales:sale_detail', kwargs={'pk': self.object.sale.pk})
    
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
            return reverse('sales:customer_detail', kwargs={'pk': self.object.customer.pk})
        return reverse('sales:sale_detail', kwargs={'pk': self.object.sale.pk})
    
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
            return reverse('sales:customer_detail', kwargs={'pk': self.object.customer.pk})
        return reverse('sales:sale_detail', kwargs={'pk': self.object.sale.pk})

class LoyaltyTransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = LoyaltyTransaction
    template_name = 'sales/loyaltytransaction_confirm_delete.html'
    
    def get_success_url(self):
        if self.object.customer:
            return reverse('sales:customer_detail', kwargs={'pk': self.object.customer.pk})
        return reverse('sales:sale_detail', kwargs={'pk': self.object.sale.pk})
    
    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        customer = transaction.customer
        
        # Reverse points before deletion
        customer.loyalty_points -= (transaction.points_earned - transaction.points_redeemed)
        customer.save()
        
        messages.success(request, 'Loyalty transaction deleted')
        return super().delete(request, *args, **kwargs)

# ====================
# SALES TRANSACTION VIEWS
# ====================

class SalesTransactionListView(ListView):
    model = SalesTransaction
    template_name = 'sales/sales_transaction_list.html'
    context_object_name = 'sales_transactions'

class CustomerOrderListView(ListView):
    model = Sale
    template_name = 'sales/customer_order_list.html'
    context_object_name = 'orders'

# ====================
# DASHBOARD AND ANALYTICS VIEWS
# ====================

class SalesDashboardView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/dashboard.html'
    context_object_name = 'recent_sales'

    def get_queryset(self):
        return Sale.objects.select_related(
            'store', 'employee', 'customer'
        ).order_by('-sale_date')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Sales KPIs
        today = datetime.date.today()
        this_month = today.replace(day=1)

        context['today_sales'] = Sale.objects.filter(
            sale_date__date=today
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0

        context['month_sales'] = Sale.objects.filter(
            sale_date__date__gte=this_month
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0

        # Combined customer count from both Customer and CustomerAccount models
        from e_commerce.models import CustomerAccount
        sales_customers_count = Customer.objects.count()
        ecommerce_customers_count = CustomerAccount.objects.count()
        context['total_customers'] = sales_customers_count + ecommerce_customers_count

        context['total_products_sold'] = SaleItem.objects.filter(
            sale__sale_date__date__gte=this_month
        ).aggregate(total=models.Sum('quantity'))['total'] or 0

        # Top products this month
        context['top_products'] = SaleItem.objects.filter(
            sale__sale_date__date__gte=this_month
        ).values('product__name').annotate(
            total_quantity=models.Sum('quantity'),
            total_revenue=models.Sum(
                models.F('quantity') * models.F('unit_price') *
                (1 - models.F('discount_percentage') / 100)
            )
        ).order_by('-total_quantity')[:5]

        # Recent returns
        context['recent_returns'] = Return.objects.select_related(
            'sale', 'employee'
        ).order_by('-return_date')[:5]

        return context

class CustomerAnalyticsView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'sales/customer_analytics.html'
    context_object_name = 'customers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Combined customer analytics from both models
        from e_commerce.models import CustomerAccount
        sales_customers_count = Customer.objects.count()
        ecommerce_customers_count = CustomerAccount.objects.count()
        context['total_customers'] = sales_customers_count + ecommerce_customers_count

        # Active customers (those with recent activity)
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        active_sales_customers = Customer.objects.filter(
            purchases__sale_date__date__gte=thirty_days_ago
        ).distinct().count()

        active_ecommerce_customers = CustomerAccount.objects.filter(
            online_orders__order_date__date__gte=thirty_days_ago
        ).distinct().count()

        context['active_customers'] = active_sales_customers + active_ecommerce_customers

        # Membership distribution (only from sales customers)
        context['membership_distribution'] = Customer.objects.values(
            'membership_level'
        ).annotate(count=models.Count('id')).order_by('-count')

        # Top customers by spending (only from sales customers)
        context['top_customers'] = Customer.objects.annotate(
            total_spent=models.Sum('purchases__total_amount')
        ).filter(total_spent__isnull=False).order_by('-total_spent')[:10]

        # Combined loyalty points distribution
        sales_loyalty_stats = Customer.objects.aggregate(
            avg=models.Avg('loyalty_points'),
            max=models.Max('loyalty_points'),
            total=models.Sum('loyalty_points')
        )

        ecommerce_loyalty_stats = CustomerAccount.objects.aggregate(
            avg=models.Avg('loyalty_points'),
            max=models.Max('loyalty_points'),
            total=models.Sum('loyalty_points')
        )

        # Combine the stats
        total_sales_points = sales_loyalty_stats['total'] or 0
        total_ecommerce_points = ecommerce_loyalty_stats['total'] or 0
        total_customers_with_points = (
            Customer.objects.filter(loyalty_points__gt=0).count() +
            CustomerAccount.objects.filter(loyalty_points__gt=0).count()
        )

        context['loyalty_stats'] = {
            'avg_points': (total_sales_points + total_ecommerce_points) / max(total_customers_with_points, 1),
            'max_points': max(sales_loyalty_stats['max'] or 0, ecommerce_loyalty_stats['max'] or 0),
            'total_points': total_sales_points + total_ecommerce_points,
        }

        return context

class PerformanceReportView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/performance_report.html'
    context_object_name = 'sales'

    def get_queryset(self):
        queryset = Sale.objects.select_related('employee', 'store')

        # Date filtering
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date:
            queryset = queryset.filter(sale_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sale_date__date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Employee performance
        context['employee_performance'] = Sale.objects.values(
            'employee__first_name', 'employee__last_name'
        ).annotate(
            total_sales=models.Count('id'),
            total_revenue=models.Sum('total_amount'),
            avg_sale=models.Avg('total_amount')
        ).order_by('-total_revenue')

        # Store performance
        context['store_performance'] = Sale.objects.values(
            'store__name'
        ).annotate(
            total_sales=models.Count('id'),
            total_revenue=models.Sum('total_amount')
        ).order_by('-total_revenue')

        # Payment method distribution
        context['payment_methods'] = Sale.objects.values(
            'payment_method'
        ).annotate(count=models.Count('id')).order_by('-count')

        return context

class ProductPerformanceView(LoginRequiredMixin, ListView):
    model = SaleItem
    template_name = 'sales/product_performance.html'
    context_object_name = 'products'

    def get_queryset(self):
        return SaleItem.objects.select_related('product', 'sale').order_by('-sale__sale_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Product performance metrics
        context['product_performance'] = SaleItem.objects.values(
            'product__name', 'product__sku'
        ).annotate(
            total_quantity=models.Sum('quantity'),
            total_revenue=models.Sum(
                models.F('quantity') * models.F('unit_price') *
                (1 - models.F('discount_percentage') / 100)
            ),
            avg_price=models.Avg('unit_price'),
            sales_count=models.Count('sale', distinct=True)
        ).order_by('-total_revenue')

        # Low stock alerts
        from inventory.models import Product
        context['low_stock_products'] = Product.objects.filter(
            stock_quantity__lte=models.F('reorder_level')
        ).select_related('category', 'brand')

        return context

class QuickSaleView(LoginRequiredMixin, CreateView):
    model = Sale
    template_name = 'sales/quick_sale.html'
    fields = ['customer', 'payment_method', 'discount_amount']

    def get_initial(self):
        initial = super().get_initial()
        initial['sale_date'] = datetime.datetime.now()
        initial['employee'] = self.request.user.employee if hasattr(self.request.user, 'employee') else None
        initial['store'] = self.request.user.employee.store if hasattr(self.request.user, 'employee') and hasattr(self.request.user.employee, 'store') else None
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Quick sale formset
        SaleItemFormSet = inlineformset_factory(
            Sale,
            SaleItem,
            fields=('product', 'quantity', 'unit_price', 'discount_percentage'),
            extra=5,
            can_delete=True
        )

        if self.request.POST:
            context['formset'] = SaleItemFormSet(self.request.POST)
        else:
            context['formset'] = SaleItemFormSet()

        # Popular products for quick selection - removed as inventory app is deleted
        context['popular_products'] = []

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            form.instance.created_by = self.request.user.employee_profile
            self.object = form.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()

                # Calculate total
                self.object.total_amount = sum(
                    item.quantity * item.unit_price * (1 - item.discount_percentage / 100)
                    for item in self.object.items.all()
                )
                self.object.save()

                # Award loyalty points if customer exists
                if self.object.customer:
                    points_earned = int(self.object.total_amount / 10)  # 1 point per $10
                    LoyaltyTransaction.objects.create(
                        customer=self.object.customer,
                        sale=self.object,
                        points_earned=points_earned,
                        transaction_date=self.object.sale_date
                    )
            else:
                return self.form_invalid(form)

        messages.success(self.request, f'Quick sale completed! Total: ${self.object.total_amount:.2f}')
        return redirect('sales:quick_sale')

class LoyaltyDashboardView(LoginRequiredMixin, ListView):
    model = LoyaltyTransaction
    template_name = 'sales/loyalty_dashboard.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return LoyaltyTransaction.objects.select_related(
            'customer', 'sale'
        ).order_by('-transaction_date')[:50]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Loyalty statistics
        context['loyalty_stats'] = {
            'total_customers': Customer.objects.filter(loyalty_points__gt=0).count(),
            'total_points_issued': LoyaltyTransaction.objects.aggregate(
                total=models.Sum('points_earned')
            )['total'] or 0,
            'total_points_redeemed': LoyaltyTransaction.objects.aggregate(
                total=models.Sum('points_redeemed')
            )['total'] or 0,
            'active_points': Customer.objects.aggregate(
                total=models.Sum('loyalty_points')
            )['total'] or 0,
        }

        # Top loyalty customers
        context['top_loyalty_customers'] = Customer.objects.filter(
            loyalty_points__gt=0
        ).order_by('-loyalty_points')[:10]

        # Recent loyalty activity
        context['recent_activity'] = LoyaltyTransaction.objects.select_related(
            'customer'
        ).order_by('-transaction_date')[:20]

        # Membership level distribution
        context['membership_levels'] = Customer.objects.values(
            'membership_level'
        ).annotate(count=models.Count('id')).order_by('-count')

        return context
