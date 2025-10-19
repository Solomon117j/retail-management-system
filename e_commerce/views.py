from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.forms import inlineformset_factory
from django.db import transaction, models
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from .models import OnlineOrder, OrderItem, CustomerAccount
from .mixins import CustomerAccessMixin
from .payment_service import PaymentService
from .serializers import GuestCheckoutSerializer
from sales.models import Customer
from inventory.models import Product, Category, Brand, InventoryRecord, StockMovement
from django.db.models import Q, Sum
import json
import stripe
from decimal import Decimal
from django.conf import settings
from rest_framework.exceptions import ValidationError as DRFValidationError

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

class OptionalLoginMixin:
    """Mixin that allows views to work for both authenticated and guest users"""
    pass

    def get_available_stock(self, product):
        """Get total available stock for a product across all stores"""
        return InventoryRecord.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0

    def get_cart_quantity(self, request, product):
        """Get current quantity of product in cart"""
        if request.user.is_authenticated:
            try:
                customer_account = CustomerAccount.objects.get(user=request.user)
                cart = customer_account.cart
                if cart:
                    cart_item = cart.items.filter(product=product).first()
                    return cart_item.quantity if cart_item else 0
            except (CustomerAccount.DoesNotExist, Cart.DoesNotExist):
                pass
        else:
            # Check session cart
            session_cart = request.session.get('guest_cart', {})
            product_id_str = str(product.id)
            return session_cart.get(product_id_str, {}).get('quantity', 0)
        return 0

    def validate_cart_stock(self, request):
        """
        Validate that all items in cart have sufficient stock
        Returns (is_valid, insufficient_items)
        """
        insufficient_items = []

        if request.user.is_authenticated:
            try:
                customer_account = CustomerAccount.objects.get(user=request.user)
                cart = customer_account.cart
                if cart:
                    for item in cart.items.select_related('product'):
                        available_stock = self.get_available_stock(item.product)
                        if item.quantity > available_stock:
                            insufficient_items.append({
                                'product': item.product,
                                'requested': item.quantity,
                                'available': available_stock
                            })
            except (CustomerAccount.DoesNotExist, Cart.DoesNotExist):
                pass
        else:
            # Check session cart
            session_cart = request.session.get('guest_cart', {})
            for product_id_str, item_data in session_cart.items():
                try:
                    product = Product.objects.get(pk=int(product_id_str), show_online=True, is_active=True)
                    available_stock = self.get_available_stock(product)
                    quantity = item_data['quantity']
                    if quantity > available_stock:
                        insufficient_items.append({
                            'product': product,
                            'requested': quantity,
                            'available': available_stock
                        })
                except Product.DoesNotExist:
                    continue

        return len(insufficient_items) == 0, insufficient_items

    def validate_order_stock(self, order):
        """
        Validate that all items in an order have sufficient stock
        Returns (is_valid, insufficient_items)
        """
        insufficient_items = []
        for item in order.items.select_related('product'):
            available_stock = self.get_available_stock(item.product)
            if item.quantity > available_stock:
                insufficient_items.append({
                    'product': item.product,
                    'requested': item.quantity,
                    'available': available_stock
                })

        return len(insufficient_items) == 0, insufficient_items

    def _decrease_stock_for_order(self, order, user):
        """Decrease stock when order is confirmed/processed"""
        for item in order.items.all():
            # Get all inventory records for this product
            inventory_records = InventoryRecord.objects.filter(product=item.product).order_by('quantity')

            remaining_quantity = item.quantity
            for record in inventory_records:
                if remaining_quantity <= 0:
                    break

                if record.quantity >= remaining_quantity:
                    # This record has enough stock
                    record.quantity -= remaining_quantity
                    if user:
                        record.last_updated_by = user.employee_profile
                    record.save()

                    # Create stock movement record
                    StockMovement.objects.create(
                        product=item.product,
                        store=record.store,
                        quantity=remaining_quantity,
                        movement_type='OUT',
                        reason='SALE',
                        reference=f'Order #{order.id}',
                        performed_by=user.employee_profile if user else None
                    )
                    remaining_quantity = 0
                else:
                    # Use all stock from this record
                    used_quantity = record.quantity
                    record.quantity = 0
                    if user:
                        record.last_updated_by = user.employee_profile
                    record.save()

                    # Create stock movement record
                    StockMovement.objects.create(
                        product=item.product,
                        store=record.store,
                        quantity=used_quantity,
                        movement_type='OUT',
                        reason='SALE',
                        reference=f'Order #{order.id}',
                        performed_by=user.employee_profile if user else None
                    )
                    remaining_quantity -= used_quantity

    def _restore_stock_for_order(self, order, user):
        """Restore stock when order is cancelled"""
        for item in order.items.all():
            # Find the store with most stock or default store for restoration
            # For simplicity, we'll add back to the first available store
            inventory_record = InventoryRecord.objects.filter(product=item.product).first()
            if inventory_record:
                inventory_record.quantity += item.quantity
                if user:
                    inventory_record.last_updated_by = user.employee_profile
                inventory_record.save()

                # Create stock movement record
                StockMovement.objects.create(
                    product=item.product,
                    store=inventory_record.store,
                    quantity=item.quantity,
                    movement_type='IN',
                    reason='CANCEL',
                    reference=f'Order #{order.id} Cancelled',
                    performed_by=user.employee_profile if user else None
                )

class OnlineOrderStatusUpdateView(LoginRequiredMixin, OptionalLoginMixin, View):
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
            with transaction.atomic():
                old_status = order.status
                order.status = new_status
                order.save()

                # Handle stock management based on status changes
                if new_status == 'processing' and old_status == 'pending':
                    # Order confirmed - decrease stock
                    self._decrease_stock_for_order(order, request.user)
                elif new_status == 'cancelled' and old_status in ['pending', 'processing']:
                    # Order cancelled - restore stock
                    self._restore_stock_for_order(order, request.user)

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
        queryset = Product.objects.filter(show_online=True, is_active=True)

        # Search filter
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(sku__icontains=q)
            )

        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Brand filter
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand_id=brand)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['brands'] = Brand.objects.all()
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_brand'] = self.request.GET.get('brand', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

class ProductDetailView(DetailView):
    model = Product
    template_name = 'e_commerce/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(show_online=True, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate total stock across all stores
        total_stock = InventoryRecord.objects.filter(product=self.object).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        if total_stock > 0:
            context['stock_status'] = f'In Stock ({total_stock} available)'
            context['stock_badge_class'] = 'bg-success'
        else:
            context['stock_status'] = 'Out of Stock'
            context['stock_badge_class'] = 'bg-danger'

        context['total_stock'] = total_stock
        return context

# Cart functionality with session support for guests
from .models import Cart, CartItem
from django.http import HttpResponse
import csv

class AddToCartView(OptionalLoginMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, pk=product_id, show_online=True, is_active=True)

        # Check stock availability
        available_stock = self.get_available_stock(product)
        current_cart_quantity = self.get_cart_quantity(request, product)
        total_requested = current_cart_quantity + quantity

        if total_requested > available_stock:
            messages.error(request, f'Insufficient stock. Only {available_stock} items available. You have {current_cart_quantity} in cart.')
            return redirect('e_commerce:product_detail', pk=product_id)

        if available_stock <= 0:
            messages.error(request, 'This product is currently out of stock.')
            return redirect('e_commerce:product_detail', pk=product_id)

        if request.user.is_authenticated:
            # Handle authenticated user cart
            try:
                customer_account = CustomerAccount.objects.get(user=request.user)
                cart, created = Cart.objects.get_or_create(customer=customer_account)

                # Check if item already in cart
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )

                if not item_created:
                    cart_item.quantity += quantity
                    cart_item.save()

                # Merge session cart if exists
                self._merge_session_cart(request, cart)

            except CustomerAccount.DoesNotExist:
                messages.error(request, 'Customer account not found')
                return redirect('e_commerce:product_browse')
        else:
            # Handle guest cart using session
            self._add_to_session_cart(request, product_id, quantity)

        messages.success(request, f'{product.name} added to cart')
        return redirect('e_commerce:cart')

    def _add_to_session_cart(self, request, product_id, quantity):
        """Add item to session-based cart for guests"""
        cart = request.session.get('guest_cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            cart[product_id_str]['quantity'] += quantity
        else:
            cart[product_id_str] = {'quantity': quantity}

        request.session['guest_cart'] = cart
        request.session.modified = True

    def _merge_session_cart(self, request, user_cart):
        """Merge session cart into user cart when logging in"""
        session_cart = request.session.get('guest_cart', {})

        for product_id_str, item_data in session_cart.items():
            try:
                product = Product.objects.get(pk=int(product_id_str), show_online=True, is_active=True)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=product,
                    defaults={'quantity': item_data['quantity']}
                )
                if not created:
                    cart_item.quantity += item_data['quantity']
                    cart_item.save()
            except Product.DoesNotExist:
                continue

        # Clear session cart after merging
        if 'guest_cart' in request.session:
            del request.session['guest_cart']

class CartView(View):
    template_name = 'e_commerce/cart.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Handle authenticated user cart
            try:
                customer_account = CustomerAccount.objects.get(user=request.user)
                cart = customer_account.cart
                cart_items = cart.items.select_related('product') if cart else CartItem.objects.none()
                total_price = cart.total_price if cart else 0
                total_items = cart.total_items if cart else 0
            except (CustomerAccount.DoesNotExist, Cart.DoesNotExist):
                cart_items = CartItem.objects.none()
                total_price = 0
                total_items = 0
        else:
            # Handle guest cart from session
            cart_items, total_price, total_items = self._get_session_cart_items(request)

        # Calculate tax for authenticated users
        if request.user.is_authenticated and cart:
            subtotal = cart.subtotal
            tax_amount = cart.tax_amount
            total_price = cart.total_price
        else:
            # Calculate tax for guest cart
            subtotal = total_price
            tax_amount = subtotal * Decimal('0.15')
            total_price = subtotal + tax_amount

        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_price': total_price,
            'total_items': total_items,
            'is_guest': not request.user.is_authenticated,
        }

        from django.shortcuts import render
        return render(request, self.template_name, context)

    def _get_session_cart_items(self, request):
        """Get cart items from session for guests"""
        session_cart = request.session.get('guest_cart', {})
        cart_items = []
        total_price = 0
        total_items = 0

        for product_id_str, item_data in session_cart.items():
            try:
                product = Product.objects.get(pk=int(product_id_str), show_online=True, is_active=True)
                quantity = item_data['quantity']
                item_total = product.unit_price * quantity

                # Create a mock cart item object for template compatibility
                class MockCartItem:
                    def __init__(self, product, quantity, item_total):
                        self.product = product
                        self.quantity = quantity
                        self.total_price = item_total

                cart_item = MockCartItem(product, quantity, item_total)
                cart_items.append(cart_item)
                total_price += item_total
                total_items += quantity

            except Product.DoesNotExist:
                continue

        return cart_items, total_price, total_items

class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        if request.user.is_authenticated:
            # Handle authenticated user cart
            cart_item = get_object_or_404(CartItem, pk=pk, cart__customer__user=request.user)
            cart_item.delete()
        else:
            # Handle guest cart from session
            product_id = pk  # pk is product_id for guests
            self._remove_from_session_cart(request, product_id)

        messages.success(request, 'Item removed from cart')
        return redirect('e_commerce:cart')

    def _remove_from_session_cart(self, request, product_id):
        """Remove item from session-based cart for guests"""
        cart = request.session.get('guest_cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            del cart[product_id_str]
            request.session['guest_cart'] = cart
            request.session.modified = True

class CheckoutView(OptionalLoginMixin, View):
    def get(self, request, *args, **kwargs):
        # Validate stock before proceeding with checkout
        is_valid, insufficient_items = self.validate_cart_stock(request)
        if not is_valid:
            for item in insufficient_items:
                messages.error(request,
                    f'Insufficient stock for {item["product"].name}. '
                    f'Requested: {item["requested"]}, Available: {item["available"]}'
                )
            return redirect('e_commerce:cart')

        if request.user.is_authenticated:
            # Handle authenticated user checkout
            customer_account = get_object_or_404(CustomerAccount, user=request.user)
            try:
                cart = customer_account.cart
                if not cart.items.exists():
                    messages.error(request, 'Your cart is empty')
                    return redirect('e_commerce:cart')

                # Create order first
                with transaction.atomic():
                    order = OnlineOrder.objects.create(
                        customer=customer_account,
                        shipping_address=customer_account.address,
                        shipping_method='standard',
                        payment_method='credit_card',
                        total_amount=cart.total_price,  # Now includes tax
                        status='pending'
                    )

                    # Create order items
                    for item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            unit_price=item.product.unit_price
                        )

                # Create payment intent
                payment_service = PaymentService()
                payment_result = payment_service.create_payment_intent(order)

                if payment_result['success']:
                    # Clear cart on successful order creation
                    cart.items.all().delete()
                    return redirect('e_commerce:payment_form', order_id=order.id)
                else:
                    # Delete order if payment intent creation failed
                    order.delete()
                    messages.error(request, f'Payment setup failed: {payment_result["error"]}')
                    return redirect('e_commerce:cart')

            except Cart.DoesNotExist:
                messages.error(request, 'No cart found')
                return redirect('e_commerce:product_browse')
        else:
            # Handle guest checkout
            session_cart = request.session.get('guest_cart', {})
            if not session_cart:
                messages.error(request, 'Your cart is empty')
                return redirect('e_commerce:cart')

            # Redirect to guest checkout form
            return redirect('e_commerce:guest_checkout')

    def post(self, request, *args, **kwargs):
        """Handle payment processing for authenticated users"""
        if not request.user.is_authenticated:
            return redirect('e_commerce:guest_checkout')

        customer_account = get_object_or_404(CustomerAccount, user=request.user)
        try:
            cart = customer_account.cart
            if not cart.items.exists():
                messages.error(request, 'Your cart is empty')
                return redirect('e_commerce:cart')

            # Create order first
            with transaction.atomic():
                order = OnlineOrder.objects.create(
                    customer=customer_account,
                    shipping_address=customer_account.address,
                    shipping_method='standard',
                    payment_method=request.POST.get('payment_method', 'credit_card'),
                    total_amount=cart.total_price,  # Now includes tax
                    status='pending'
                )

                # Create order items
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.unit_price
                    )

            # Process payment
            payment_data = {
                'card_number': request.POST.get('card_number', ''),
                'expiry_month': request.POST.get('expiry_month', ''),
                'expiry_year': request.POST.get('expiry_year', ''),
                'cvv': request.POST.get('cvv', ''),
                'card_holder_name': request.POST.get('card_holder_name', ''),
                'wallet_id': request.POST.get('wallet_id', ''),
            }

            payment_result = PaymentService().process_payment(order, payment_data)

            if payment_result['success']:
                # Decrement stock immediately upon successful payment
                self._decrease_stock_for_order(order, request.user)

                # Clear cart on successful payment
                cart.items.all().delete()
                messages.success(request, f'Payment successful! Order #{order.id} created successfully')
                return redirect('e_commerce:order_detail', pk=order.pk)
            else:
                # Payment failed - delete the order
                order.delete()
                messages.error(request, f'Payment failed: {payment_result["error"]}')
                return redirect('e_commerce:payment_form')

        except Cart.DoesNotExist:
            messages.error(request, 'No cart found')
            return redirect('e_commerce:product_browse')
        except Exception as e:
            messages.error(request, f'An error occurred during checkout: {str(e)}')
            return redirect('e_commerce:cart')

class GuestCheckoutView(OptionalLoginMixin, View):
    template_name = 'e_commerce/guest_checkout.html'

    def get(self, request, *args, **kwargs):
        # Check if user is authenticated - redirect to regular checkout
        if request.user.is_authenticated:
            return redirect('e_commerce:checkout')

        # Check if cart is empty
        session_cart = request.session.get('guest_cart', {})
        if not session_cart:
            messages.error(request, 'Your cart is empty')
            return redirect('e_commerce:cart')

        # Calculate total for display
        total_amount = 0
        cart_items = []
        for product_id_str, item_data in session_cart.items():
            try:
                product = Product.objects.get(pk=int(product_id_str), show_online=True, is_active=True)
                quantity = item_data['quantity']
                item_total = product.unit_price * quantity
                total_amount += item_total
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': product.unit_price,
                    'total_price': item_total
                })
            except Product.DoesNotExist:
                continue

        context = {
            'cart_items': cart_items,
            'total_amount': total_amount,
            'shipping_methods': OnlineOrder.SHIPPING_METHOD_CHOICES,
            'payment_methods': OnlineOrder.PAYMENT_METHOD_CHOICES,
        }

        from django.shortcuts import render
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Process guest checkout form submission with payment using serializer
        session_cart = request.session.get('guest_cart', {})
        if not session_cart:
            messages.error(request, 'Your cart is empty')
            return redirect('e_commerce:cart')

        # Use serializer for validation
        serializer = GuestCheckoutSerializer(data=request.POST)
        if not serializer.is_valid():
            # Display serializer errors as messages
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect('e_commerce:guest_checkout')

        try:
            # Create order using serializer
            order = serializer.create_order(request)

            # Process payment
            payment_data = serializer.get_payment_data()
            payment_result = PaymentService().process_payment(order, payment_data)

            if payment_result['success']:
                # Decrement stock immediately upon successful payment
                self._decrease_stock_for_order(order, None)  # No user for guest checkout

                # Clear session cart on successful payment
                del request.session['guest_cart']
                messages.success(request, f'Payment successful! Order #{order.id} created successfully')
                return redirect('e_commerce:order_detail', pk=order.pk)
            else:
                # Payment failed - delete the order
                order.delete()
                messages.error(request, f'Payment failed: {payment_result["error"]}')
                return redirect('e_commerce:guest_checkout')

        except DRFValidationError as e:
            # Handle serializer validation errors during order creation
            for field, errors in e.detail.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect('e_commerce:guest_checkout')
        except Exception as e:
            messages.error(request, f'An error occurred during checkout: {str(e)}')
            return redirect('e_commerce:guest_checkout')

class PaymentFormView(LoginRequiredMixin, View):
    template_name = 'e_commerce/payment_form.html'

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        if not order_id:
            messages.error(request, 'Order ID is required')
            return redirect('e_commerce:cart')

        order = get_object_or_404(OnlineOrder, pk=order_id, customer__user=request.user)

        # Check if payment intent already exists
        payment_service = PaymentService()
        if order.payment_transaction_id:
            payment_result = payment_service.retrieve_payment_intent(order.payment_transaction_id)
            if payment_result['success']:
                client_secret = payment_result['payment_intent'].client_secret
            else:
                # Create new payment intent if retrieval failed
                payment_result = payment_service.create_payment_intent(order)
                if payment_result['success']:
                    client_secret = payment_result['client_secret']
                else:
                    messages.error(request, f'Payment setup failed: {payment_result["error"]}')
                    return redirect('e_commerce:cart')
        else:
            # Create payment intent
            payment_result = payment_service.create_payment_intent(order)
            if payment_result['success']:
                client_secret = payment_result['client_secret']
            else:
                messages.error(request, f'Payment setup failed: {payment_result["error"]}')
                return redirect('e_commerce:cart')

        # Calculate totals for display
        cart_items = order.items.select_related('product')
        total_price = order.total_amount
        total_items = sum(item.quantity for item in order.items.all())

        context = {
            'order': order,
            'cart_items': cart_items,
            'total_price': total_price,
            'total_items': total_items,
            'payment_methods': OnlineOrder.PAYMENT_METHOD_CHOICES,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': client_secret,
        }

        return render(request, self.template_name, context)

class PaymentWebhookView(View):
    """
    Handle Stripe webhook events
    """
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        if not sig_header:
            return JsonResponse({'error': 'Missing signature'}, status=400)

        payment_service = PaymentService()
        result = payment_service.handle_webhook(payload, sig_header)

        if result['success']:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'error': result.get('error', 'Webhook processing failed')}, status=400)

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
                f'SZL {order.total_amount}',
                order.get_shipping_method_display()
            ])

        return response
