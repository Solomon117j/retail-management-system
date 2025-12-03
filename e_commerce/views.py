# ecommerce/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, JsonResponse
from django.forms import inlineformset_factory
from django.db import transaction, models
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
from django.conf import settings
from .models import OnlineOrder, OrderItem, CustomerAccount

logger = logging.getLogger(__name__)
from .mixins import CustomerAccessMixin
from .mtn_momo_utils import create_mtn_momo_payment, verify_mtn_momo_payment
from .payfast_utils import create_payfast_payment, process_payfast_notification
from .mygate_utils import create_mygate_payment, verify_mygate_payment, process_mygate_webhook
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_name'] = self.template_name
        return context

class CustomerAccountUpdateView(LoginRequiredMixin, CustomerAccessMixin, UpdateView):
    model = CustomerAccount
    template_name = 'e_commerce/customer_account_form.html'
    fields = ['first_name', 'last_name', 'phone', 'address', 'birth_date', 'preferred_language', 'marketing_opt_in', 'sms_notifications', 'push_notifications']
    success_url = reverse_lazy('e_commerce:customer_account_list')

    def get_object(self, queryset=None):
        # Get the customer account object for the logged-in user
        return super().get_object(queryset)

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully.')
        return super().form_valid(form)

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
            fields=('product_name', 'quantity', 'unit_price'),
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
            form.instance.created_by = self.request.user.employee_profile
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
            fields=('product_name', 'quantity', 'unit_price'),
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
        context['items'] = self.object.items.all()
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
        from inventory.models import Product, Category, Brand
        queryset = Product.objects.filter(
            is_active=True,
            inventory_records__quantity__gt=0
        ).select_related('category', 'brand').distinct()

        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        brand_id = self.request.GET.get('brand')

        if q:
            queryset = queryset.filter(name__icontains=q)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        return queryset

    def get_context_data(self, **kwargs):
        from inventory.models import Category, Brand
        from django.db.models import Sum
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['brands'] = Brand.objects.all()
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_brand'] = self.request.GET.get('brand', '')
        ctx['q'] = self.request.GET.get('q', '')

        # Add stock information for each product
        for product in ctx['products']:
            total_stock = product.inventory_records.aggregate(total=Sum('quantity'))['total'] or 0
            product.total_stock = total_stock
            if total_stock > 10:
                product.stock_status = 'In Stock'
                product.stock_badge_class = 'bg-success'
            elif total_stock > 0:
                product.stock_status = 'Low Stock'
                product.stock_badge_class = 'bg-warning'
            else:
                product.stock_status = 'Out of Stock'
                product.stock_badge_class = 'bg-danger'

        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'e_commerce/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        from inventory.models import Product
        return Product.objects.filter(
            is_active=True,
            inventory_records__quantity__gt=0
        ).select_related('category', 'brand').distinct()

    def get_context_data(self, **kwargs):
        from django.db.models import Sum
        context = super().get_context_data(**kwargs)
        total_stock = self.object.inventory_records.aggregate(total=Sum('quantity'))['total'] or 0
        context['total_stock'] = total_stock
        if total_stock > 0:
            context['stock_status'] = 'In Stock'
            context['stock_badge_class'] = 'bg-success'
        else:
            context['stock_status'] = 'Out of Stock'
            context['stock_badge_class'] = 'bg-danger'
        return context

# Make sure this model exists

from .models import Cart, CartItem
from django.http import HttpResponse
import csv

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        from inventory.models import Product
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, pk=product_id, is_active=True)
        if not product.inventory_records.filter(quantity__gt=0).exists():
            raise Http404("Product out of stock")

        # Check if product has sufficient stock
        total_stock = product.inventory_records.aggregate(total=models.Sum('quantity'))['total'] or 0
        if quantity > total_stock:
            messages.error(request, f'Insufficient stock. Only {total_stock} items available.')
            return redirect('e_commerce:product_detail', pk=product.pk)

        if request.user.is_authenticated:
            # Handle authenticated user cart
            customer_account = get_object_or_404(CustomerAccount, user=request.user)
            cart, created = Cart.objects.get_or_create(customer=customer_account)

            # Check if item already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'unit_price': product.unit_price}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        else:
            # Handle guest cart using session
            cart = request.session.get('guest_cart', {})
            product_key = str(product.pk)

            if product_key in cart:
                cart[product_key]['quantity'] += quantity
            else:
                cart[product_key] = {
                    'product_id': product.pk,
                    'product_name': product.name,
                    'unit_price': str(product.unit_price),
                    'quantity': quantity
                }

            request.session['guest_cart'] = cart
            request.session.modified = True

        messages.success(request, f'{product.name} added to cart.')
        return redirect('e_commerce:cart')

class CartView(View):
    template_name = 'e_commerce/cart.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Handle authenticated user cart
            try:
                customer_account = CustomerAccount.objects.get(user=request.user)
                try:
                    cart = customer_account.cart
                    cart_items = cart.items.select_related('product')
                    total_price = cart.total_price
                    total_items = cart.total_items
                except Cart.DoesNotExist:
                    cart_items = []
                    total_price = 0
                    total_items = 0
            except CustomerAccount.DoesNotExist:
                # User doesn't have a customer account yet
                messages.info(request, 'Please complete your customer profile to access cart functionality.')
                return redirect('e_commerce:customer_account_list')  # Redirect to account management
        else:
            # Handle guest cart from session
            guest_cart = request.session.get('guest_cart', {})
            cart_items = []
            total_price = 0
            total_items = 0

            for product_id, item_data in guest_cart.items():
                try:
                    product = Product.objects.get(pk=item_data['product_id'])
                    item_total = float(item_data['unit_price']) * item_data['quantity']
                    total_price += item_total
                    total_items += item_data['quantity']
                    cart_items.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'unit_price': float(item_data['unit_price']),
                        'total_price': item_total,
                        'product_name': item_data['product_name']
                    })
                except Product.DoesNotExist:
                    continue  # Skip invalid products

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'total_items': total_items,
            'is_guest': not request.user.is_authenticated
        }
        return render(request, self.template_name, context)

class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            product_id = request.POST.get('product_id')
            if product_id:
                try:
                    customer_account = CustomerAccount.objects.get(user=request.user)
                    cart = customer_account.cart
                    cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                    cart_item.delete()
                except (CustomerAccount.DoesNotExist, Cart.DoesNotExist, CartItem.DoesNotExist):
                    pass  # Item not found, do nothing
        else:
            # Handle guest cart removal
            product_id = request.POST.get('product_id')
            if product_id:
                guest_cart = request.session.get('guest_cart', {})
                if product_id in guest_cart:
                    del guest_cart[product_id]
                    request.session['guest_cart'] = guest_cart
                    request.session.modified = True
        messages.success(request, 'Item removed from cart')
        return redirect('e_commerce:cart')

class CheckoutView(View):
    template_name = 'e_commerce/checkout.html'

    def get(self, request, *args, **kwargs):
        # Get cart items for both authenticated and guest users
        if request.user.is_authenticated:
            try:
                customer_account = CustomerAccount.objects.get(user=request.user)
                try:
                    cart = customer_account.cart
                    cart_items = cart.items.select_related('product')
                    total_price = cart.total_price
                    total_items = cart.total_items
                except Cart.DoesNotExist:
                    cart_items = []
                    total_price = 0
                    total_items = 0
            except CustomerAccount.DoesNotExist:
                messages.info(request, 'Please complete your customer profile to checkout.')
                return redirect('e_commerce:customer_account_list')
        else:
            # Handle guest cart from session
            guest_cart = request.session.get('guest_cart', {})
            cart_items = []
            total_price = 0
            total_items = 0

            for product_id, item_data in guest_cart.items():
                try:
                    product = Product.objects.get(pk=item_data['product_id'])
                    item_total = float(item_data['unit_price']) * item_data['quantity']
                    total_price += item_total
                    total_items += item_data['quantity']
                    cart_items.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'unit_price': float(item_data['unit_price']),
                        'total_price': item_total,
                        'product_name': item_data['product_name']
                    })
                except Product.DoesNotExist:
                    continue  # Skip invalid products

        if not cart_items:
            messages.error(request, 'Your cart is empty')
            return redirect('e_commerce:cart')

        # Check stock availability for all items
        for item in cart_items:
            total_stock = item['product'].inventory_records.aggregate(total=models.Sum('quantity'))['total'] or 0
            if item['quantity'] > total_stock:
                messages.error(request, f'Insufficient stock for {item["product"].name}. Only {total_stock} items available.')
                return redirect('e_commerce:cart')

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'total_items': total_items,
            'is_guest': not request.user.is_authenticated,
            'shipping_methods': OnlineOrder.SHIPPING_METHOD_CHOICES,
            'payment_methods': OnlineOrder.PAYMENT_METHOD_CHOICES,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Get cart items
        if request.user.is_authenticated:
            try:
                customer_account = CustomerAccount.objects.get(user=request.user)
                try:
                    cart = customer_account.cart
                    cart_items = cart.items.select_related('product')
                except Cart.DoesNotExist:
                    messages.error(request, 'No cart found')
                    return redirect('e_commerce:cart')
            except CustomerAccount.DoesNotExist:
                messages.info(request, 'Please complete your customer profile to checkout.')
                return redirect('e_commerce:customer_account_list')
        else:
            # Handle guest cart from session
            guest_cart = request.session.get('guest_cart', {})
            cart_items = []

            for product_id, item_data in guest_cart.items():
                try:
                    product = Product.objects.get(pk=item_data['product_id'])
                    cart_items.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'unit_price': float(item_data['unit_price']),
                        'product_name': item_data['product_name']
                    })
                except Product.DoesNotExist:
                    continue

        if not cart_items:
            messages.error(request, 'Your cart is empty')
            return redirect('e_commerce:cart')

        # Validate form data
        required_fields = ['shipping_address', 'shipping_method', 'payment_method']
        if not request.user.is_authenticated:
            required_fields.extend(['guest_first_name', 'guest_last_name', 'guest_email'])

        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f'{field.replace("_", " ").title()} is required.')
                return redirect('e_commerce:checkout')

        # Check stock availability again
        for item in cart_items:
            total_stock = item['product'].inventory_records.aggregate(total=models.Sum('quantity'))['total'] or 0
            if item['quantity'] > total_stock:
                messages.error(request, f'Insufficient stock for {item["product"].name}. Only {total_stock} items available.')
                return redirect('e_commerce:cart')

        # Create order
        with transaction.atomic():
            order_data = {
                'shipping_address': request.POST['shipping_address'],
                'shipping_method': request.POST['shipping_method'],
                'payment_method': request.POST['payment_method'],
                'payment_status': 'pending',
                'total_amount': sum(item['quantity'] * item['unit_price'] for item in cart_items),
            }

            if request.user.is_authenticated:
                order_data['customer'] = customer_account
            else:
                order_data.update({
                    'guest_first_name': request.POST['guest_first_name'],
                    'guest_last_name': request.POST['guest_last_name'],
                    'guest_email': request.POST['guest_email'],
                    'guest_phone': request.POST.get('guest_phone', ''),
                })

            order = OnlineOrder.objects.create(**order_data)

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price']
                )

            # Handle payment gateway integration
            payment_method = request.POST['payment_method']
            try:
                if payment_method == 'mtn_momo':
                    # Get phone number from form or customer
                    phone_number = request.POST.get('mtn_phone')
                    if not phone_number:
                        if request.user.is_authenticated and order.customer and order.customer.phone:
                            phone_number = order.customer.phone
                        elif order.guest_phone:
                            phone_number = order.guest_phone
                        else:
                            raise ValueError("Phone number is required for MTN Mobile Money payment")

                    # Update order with phone number
                    if not order.customer:
                        order.guest_phone = phone_number
                        order.save()

                    payment_result = create_mtn_momo_payment(order)
                    # For MTN MoMo, redirect to success page and handle async payment
                    messages.success(request, f'Order #{order.id} created. Please complete payment via MTN Mobile Money.')
                    return redirect('e_commerce:checkout_success')

                elif payment_method == 'payfast':
                    payment_result = create_payfast_payment(order)
                    # Redirect to PayFast payment page
                    return redirect(payment_result['payment_url'])

                elif payment_method == 'mygate':
                    payment_result = create_mygate_payment(order)
                    # Redirect to MyGate payment page
                    return redirect(payment_result['payment_url'])

                else:
                    # For traditional payment methods (credit_card, debit_card, digital_wallet)
                    # Mark as completed since payment processing is handled separately
                    order.payment_status = 'completed'
                    order.save()

            except Exception as e:
                messages.error(request, f'Payment setup failed: {str(e)}')
                return redirect('e_commerce:checkout')

            # Clear cart
            if request.user.is_authenticated:
                cart.items.all().delete()
            else:
                request.session['guest_cart'] = {}
                request.session.modified = True

        messages.success(request, f'Order #{order.id} created successfully')
        return redirect('e_commerce:order_detail', pk=order.pk)



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

def checkout_success(request):
    """Handle successful checkout return from Stripe"""
    return render(request, 'e_commerce/checkout_success.html')

@method_decorator(csrf_exempt, name='dispatch')
class PayFastNotifyView(View):
    """Handle PayFast Instant Transaction Notification (ITN)"""

    def post(self, request, *args, **kwargs):
        try:
            # Get POST data
            post_data = request.POST.dict()

            # Process the notification
            result = process_payfast_notification(post_data)

            if result['status'] == 'valid':
                # Update order status
                order_id = result['order_id']
                order = get_object_or_404(OnlineOrder, id=order_id)

                if result['payment_status'] == 'COMPLETE':
                    order.payment_status = 'completed'
                    order.status = 'processing'  # Move to processing after payment
                    order.save()
                    logger.info(f"PayFast payment completed for Order #{order_id}")
                else:
                    logger.warning(f"PayFast payment status: {result['payment_status']} for Order #{order_id}")

                # Return success response to PayFast
                return HttpResponse('SUCCESS')

            else:
                logger.error(f"Invalid PayFast notification: {result}")
                return HttpResponse('FAILED', status=400)

        except Exception as e:
            logger.error(f"Error processing PayFast notification: {str(e)}")
            return HttpResponse('FAILED', status=500)

@method_decorator(csrf_exempt, name='dispatch')
class MTNMoMoVerifyView(View):
    """Handle MTN MoMo payment verification"""

    def post(self, request, *args, **kwargs):
        try:
            order_id = request.POST.get('order_id')
            reference_id = request.POST.get('reference_id')

            if not order_id or not reference_id:
                return JsonResponse({'error': 'order_id and reference_id are required'}, status=400)

            order = get_object_or_404(OnlineOrder, id=order_id)

            # Verify the payment
            verification_result = verify_mtn_momo_payment(order, reference_id)

            if verification_result is True:
                return JsonResponse({'status': 'success', 'message': 'Payment verified successfully'})
            elif verification_result is False:
                return JsonResponse({'status': 'failed', 'message': 'Payment failed'})
            else:
                return JsonResponse({'status': 'pending', 'message': 'Payment still processing'})

        except Exception as e:
            logger.error(f"Error verifying MTN MoMo payment: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class MyGateWebhookView(View):
    """Handle MyGate webhook notifications"""

    def post(self, request, *args, **kwargs):
        try:
            # Get webhook data
            webhook_data = json.loads(request.body)

            # Process the webhook
            result = process_mygate_webhook(webhook_data)

            if result['status'] == 'error':
                logger.error(f"MyGate webhook processing failed: {result['error']}")
                return JsonResponse({'error': result['error']}, status=400)

            # Update order if reference is provided
            order_reference = result.get('order_reference')
            if order_reference:
                try:
                    order = OnlineOrder.objects.get(id=order_reference)
                    if result['status'] == 'COMPLETED':
                        order.payment_status = 'completed'
                        order.status = 'processing'
                        order.save()
                        logger.info(f"MyGate payment completed for Order #{order_reference}")
                    elif result['status'] == 'FAILED':
                        order.payment_status = 'failed'
                        order.save()
                        logger.warning(f"MyGate payment failed for Order #{order_reference}")
                except OnlineOrder.DoesNotExist:
                    logger.error(f"Order not found for MyGate webhook: {order_reference}")

            return JsonResponse({'status': 'received'})

        except json.JSONDecodeError:
            logger.error("Invalid JSON in MyGate webhook")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error processing MyGate webhook: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
