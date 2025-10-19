from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import OnlineOrder, OrderItem
from inventory.models import Product
import re


class GuestCheckoutSerializer(serializers.Serializer):
    """
    Serializer for guest checkout data validation and processing
    """

    # Basic guest information (required)
    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=True, max_length=50)
    last_name = serializers.CharField(required=True, max_length=50)
    phone = serializers.CharField(required=True, max_length=20)

    # Shipping information (required)
    shipping_address = serializers.CharField(required=True, max_length=200)
    shipping_method = serializers.ChoiceField(
        choices=OnlineOrder.SHIPPING_METHOD_CHOICES,
        required=True
    )

    # Payment information (required)
    payment_method = serializers.ChoiceField(
        choices=OnlineOrder.PAYMENT_METHOD_CHOICES,
        required=True
    )
    card_number = serializers.CharField(required=True, max_length=19, write_only=True)
    expiry_month = serializers.IntegerField(required=True, min_value=1, max_value=12, write_only=True)
    expiry_year = serializers.IntegerField(required=True, min_value=timezone.now().year, write_only=True)
    cvv = serializers.CharField(required=True, min_length=3, max_length=4, write_only=True)
    card_holder_name = serializers.CharField(required=True, max_length=100, write_only=True)

    # Enhanced guest information (optional)
    company = serializers.CharField(required=False, max_length=100, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    preferred_language = serializers.ChoiceField(
        choices=[('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('si', 'siSwati')],
        required=False,
        default='en'
    )

    # Billing address (optional - separate from shipping)
    billing_address = serializers.CharField(required=False, max_length=200, allow_blank=True)
    billing_city = serializers.CharField(required=False, max_length=100, allow_blank=True)
    billing_state = serializers.CharField(required=False, max_length=100, allow_blank=True)
    billing_postal_code = serializers.CharField(required=False, max_length=20, allow_blank=True)
    billing_country = serializers.CharField(required=False, max_length=100, allow_blank=True)

    # Marketing and communication preferences (optional)
    marketing_opt_in = serializers.BooleanField(required=False, default=False)
    sms_notifications = serializers.BooleanField(required=False, default=False)
    push_notifications = serializers.BooleanField(required=False, default=True)

    # Order customization (optional)
    order_notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    gift_wrapping = serializers.BooleanField(required=False, default=False)
    gift_message = serializers.CharField(required=False, allow_blank=True, max_length=500)
    loyalty_program_signup = serializers.BooleanField(required=False, default=False)

    def validate_card_number(self, value):
        """Validate credit card number format"""
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s-]', '', value)

        # Check if it's all digits and reasonable length
        if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
            raise serializers.ValidationError("Invalid credit card number format.")

        # Basic Luhn algorithm check
        if not self._luhn_checksum(cleaned):
            raise serializers.ValidationError("Invalid credit card number.")

        return cleaned

    def validate_expiry_year(self, value):
        """Validate expiry year is not in the past"""
        current_year = timezone.now().year
        if value < current_year:
            raise serializers.ValidationError("Card has expired.")
        return value

    def validate(self, data):
        """Cross-field validation"""
        # If billing address is provided, ensure all billing fields are present
        billing_fields = ['billing_city', 'billing_state', 'billing_postal_code', 'billing_country']
        if data.get('billing_address') and not all(data.get(field) for field in billing_fields):
            raise serializers.ValidationError({
                'billing_address': 'All billing address fields must be provided if billing address is specified.'
            })

        # Validate expiry date combination
        if 'expiry_month' in data and 'expiry_year' in data:
            current_date = timezone.now().date()
            expiry_date = data['expiry_year'] * 12 + data['expiry_month']
            current_months = current_date.year * 12 + current_date.month

            if expiry_date < current_months:
                raise serializers.ValidationError("Card has expired.")

        # Validate gift message if gift wrapping is selected
        if data.get('gift_wrapping') and not data.get('gift_message'):
            raise serializers.ValidationError({
                'gift_message': 'Gift message is required when gift wrapping is selected.'
            })

        return data

    def _luhn_checksum(self, card_number):
        """Luhn algorithm for credit card validation"""
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0

    def create_order(self, request):
        """
        Create the order using validated data
        Returns the created order instance
        """
        validated_data = self.validated_data
        session_cart = request.session.get('guest_cart', {})

        if not session_cart:
            raise serializers.ValidationError("No items in cart.")

        # Calculate total amount
        total_amount = 0
        for product_id_str, item_data in session_cart.items():
            try:
                product = Product.objects.get(pk=int(product_id_str), show_online=True, is_active=True)
                total_amount += product.unit_price * item_data['quantity']
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product {product_id_str} not found or not available.")

        # Add gift wrapping cost if selected
        if validated_data.get('gift_wrapping'):
            total_amount += 50.00  # Gift wrapping cost

        # Create the order
        order = OnlineOrder.objects.create(
            # Basic guest info
            guest_email=validated_data['email'],
            guest_first_name=validated_data['first_name'],
            guest_last_name=validated_data['last_name'],
            guest_phone=validated_data['phone'],

            # Shipping
            shipping_address=validated_data['shipping_address'],
            shipping_method=validated_data['shipping_method'],
            payment_method=validated_data['payment_method'],

            # Total and status
            total_amount=total_amount,
            status='pending',

            # Enhanced guest info
            guest_company=validated_data.get('company', ''),
            guest_birth_date=validated_data.get('birth_date'),
            guest_preferred_language=validated_data.get('preferred_language', 'en'),

            # Billing address
            billing_address=validated_data.get('billing_address', ''),
            billing_city=validated_data.get('billing_city', ''),
            billing_state=validated_data.get('billing_state', ''),
            billing_postal_code=validated_data.get('billing_postal_code', ''),
            billing_country=validated_data.get('billing_country', ''),

            # Marketing preferences
            guest_marketing_opt_in=validated_data.get('marketing_opt_in', False),
            guest_sms_notifications=validated_data.get('sms_notifications', False),
            guest_push_notifications=validated_data.get('push_notifications', True),

            # Order customization
        )

        # Create order items
        for product_id_str, item_data in session_cart.items():
            try:
                product = Product.objects.get(pk=int(product_id_str), show_online=True, is_active=True)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    unit_price=product.unit_price
                )
            except Product.DoesNotExist:
                # This shouldn't happen as we validated above, but just in case
                order.delete()
                raise serializers.ValidationError(f"Product {product_id_str} not found.")

        return order

    def get_payment_data(self):
        """Extract payment data for processing"""
        return {
            'card_number': self.validated_data['card_number'],
            'expiry_month': self.validated_data['expiry_month'],
            'expiry_year': self.validated_data['expiry_year'],
            'cvv': self.validated_data['cvv'],
            'card_holder_name': self.validated_data['card_holder_name'],
        }
