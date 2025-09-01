# ecommerce/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OnlineOrder, OrderItem, CustomerAccount
from .mixins import CustomerAccessMixin
from sales.models import Customer
from inventory.models import Product

class CustomerAccountListView(LoginRequiredMixin, ListView):
    model = CustomerAccount
    template_name = 'e_commerce/customer_account_list.html'
    context_object_name = 'customer_accounts'

    def get_queryset(self):
        # Filter to only show the logged-in user's customer account
        return CustomerAccount.objects.filter(user=self.request.user)

class CustomerAccountDetailView(LoginRequiredMixin, CustomerAccessMixin, DetailView):
    model = CustomerAccount
    template_name = 'e_commerce/customer_account_detail.html'
    context_object_name = 'account'
    
    def get_object(self, queryset=None):
        # Get the customer account object
        return super().get_object(queryset)

class OnlineOrderListView(LoginRequiredMixin, ListView):
    model = OnlineOrder
    template_name = 'e_commerce/order_list.html'
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
    template_name = 'e_commerce/order_form.html'
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
        return redirect('e_commerce:order_detail', pk=self.object.pk)

class OnlineOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = OnlineOrder
    template_name = 'e_commerce/order_form.html'
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
        return redirect('e_commerce:order_detail', pk=self.object.pk)

class OnlineOrderDetailView(LoginRequiredMixin, DetailView):
    model = OnlineOrder
    template_name = 'e_commerce/order_detail.html'
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
        
        return redirect('e_commerce:order_detail', pk=order.pk)

class OnlineOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = OnlineOrder
    template_name = 'e_commerce/order_confirm_delete.html'
    success_url = reverse_lazy('e_commerce:online_order_list')
    
    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        messages.success(request, f'Online Order #{order.id} deleted successfully')
        return super().delete(request, *args, **kwargs)

class ProductBrowseView(ListView):
    model = Product
    template_name = 'e_commerce/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        # Base: in stock in any store AND marked available online
        queryset = Product.objects.filter(
            inventory_records__quantity__gt=0,
            available_online=True,
        ).select_related('category', 'brand').distinct()

        # Filters: search, category, brand
        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        brand_id = self.request.GET.get('brand')
        if q:
            queryset = queryset.filter(name__icontains=q)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        return queryset.distinct().order_by('name')

    def get_context_data(self, **kwargs):
        from inventory.models import Category, Brand
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all().order_by('name')
        ctx['brands'] = Brand.objects.all().order_by('name')
        ctx['selected_category'] = self.request.GET.get('category') or ''
        ctx['selected_brand'] = self.request.GET.get('brand') or ''
        ctx['q'] = self.request.GET.get('q') or ''
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'e_commerce/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        # Only show products that are available online and in stock
        return Product.objects.filter(
            inventory_records__quantity__gt=0,
            available_online=True,
        ).select_related('category', 'brand').distinct()

# Make sure this model exists

from .models import Cart, CartItem
from django.http import HttpResponse
import csv

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        # Get product by pk and available_online
        product = get_object_or_404(Product, pk=product_id, available_online=True)

        # Check if product has inventory in any store
        has_inventory = product.inventory_records.filter(quantity__gt=0).exists()
        if not has_inventory:
            messages.error(request, f'Product "{product.name}" is out of stock.')
            return redirect('e_commerce:product_detail', pk=product.pk)

        # Get or create cart for the customer
        customer_account = get_object_or_404(CustomerAccount, user=request.user)
        cart, created = Cart.objects.get_or_create(customer=customer_account)

        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f'Added {quantity} x {product.name} to cart')
        return redirect('e_commerce:cart')

class CartView(LoginRequiredMixin, ListView):
    template_name = 'e_commerce/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        customer_account = get_object_or_404(CustomerAccount, user=self.request.user)
        try:
            cart = customer_account.cart
            return cart.items.select_related('product')
        except Cart.DoesNotExist:
            return CartItem.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_account = get_object_or_404(CustomerAccount, user=self.request.user)
        try:
            cart = customer_account.cart
            context['cart'] = cart
            context['total_price'] = cart.total_price
            context['total_items'] = cart.total_items
        except Cart.DoesNotExist:
            context['cart'] = None
            context['total_price'] = 0
            context['total_items'] = 0
        return context

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart_item_id = kwargs['pk']
        cart_item = get_object_or_404(CartItem, pk=cart_item_id, cart__customer__user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
        return redirect('e_commerce:cart')

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        customer_account = get_object_or_404(CustomerAccount, user=request.user)
        try:
            cart = customer_account.cart
            if not cart.items.exists():
                messages.error(request, 'Your cart is empty')
                return redirect('e_commerce:cart')
            # For simplicity, create order from cart
            with transaction.atomic():
                order = OnlineOrder.objects.create(
                    customer=customer_account,
                    shipping_address=customer_account.address,
                    shipping_method='standard',
                    payment_method='credit_card',
                    total_amount=cart.total_price
                )
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.unit_price
                    )
                cart.items.all().delete()  # Clear cart
            messages.success(request, f'Order #{order.id} created successfully')
            return redirect('e_commerce:order_detail', pk=order.pk)
        except Cart.DoesNotExist:
            messages.error(request, 'No cart found')
            return redirect('e_commerce:product_browse')

class OrderExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # For customers, export their own orders
        customer_account = get_object_or_404(CustomerAccount, user=request.user)
        orders = OnlineOrder.objects.filter(customer=customer_account).select_related('customer')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'

        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Date', 'Status', 'Total Amount', 'Shipping Method'])

        for order in orders:
            writer.writerow([
                str(order.id),
                order.order_date.strftime('%Y-%m-%d %H:%M'),
                order.get_status_display(),
                f'SZL{order.total_amount}',
                order.get_shipping_method_display()
            ])

        return response
