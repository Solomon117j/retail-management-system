from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Customer, Sale, SaleItem, Return, LoyaltyTransaction
from store_management.models import Store
from human_resources.models import Employee
from inventory.models import Product


class CustomerForm(forms.ModelForm):
    """Enhanced Customer form with validation styling and custom validation."""

    class Meta:
        model = Customer
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'country', 'state', 'join_date',
            'date_of_birth', 'gender', 'social_media',
            'preferred_contact_method', 'marketing_opt_in',
            'occupation', 'marital_status', 'number_of_dependents',
            'referral_source', 'emergency_contact_name', 'emergency_contact_phone',
            'language_preference', 'data_processing_consent',
            'email_notifications', 'sms_notifications', 'push_notifications',
            'notes', 'membership_level'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'customer@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal/ZIP code'
            }),
            'join_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'social_media': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@username or handle'
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marketing_opt_in': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about the customer'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle name (optional)'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Occupation/Job title'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'number_of_dependents': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'referral_source': forms.Select(attrs={
                'class': 'form-control'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'language_preference': forms.Select(attrs={
                'class': 'form-control'
            }),
            'data_processing_consent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'push_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'membership_level': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check for duplicate email
            queryset = Customer.objects.filter(email__iexact=email)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("A customer with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, phone))
            if len(digits_only) < 10:
                raise ValidationError("Phone number must contain at least 10 digits.")
        return phone

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get('emergency_contact_phone')
        if phone:
            # Remove all non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, phone))
            if len(digits_only) < 10:
                raise ValidationError("Emergency contact phone number must contain at least 10 digits.")
        return phone

    def clean_data_processing_consent(self):
        consent = self.cleaned_data.get('data_processing_consent')
        if not consent:
            raise ValidationError("Data processing consent is required.")
        return consent


class SaleForm(forms.ModelForm):
    """Enhanced Sale form with validation and business logic."""

    class Meta:
        model = Sale
        fields = [
            'store', 'employee', 'customer',
            'sale_date', 'payment_method',
            'discount_amount', 'tax_amount',
            'sales_channel', 'order_status',
            'notes', 'delivery_address', 'invoice_number'
        ]
        widgets = {
            'store': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'employee': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'customer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sale_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'sales_channel': forms.Select(attrs={
                'class': 'form-control'
            }),
            'order_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about the sale'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Delivery address if different from customer address'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter stores and employees based on user permissions if needed
        if self.user:
            # Add any user-specific filtering here
            pass

    def clean_sale_date(self):
        sale_date = self.cleaned_data.get('sale_date')
        if sale_date and sale_date > timezone.now():
            raise ValidationError("Sale date cannot be in the future.")
        return sale_date

    def clean_discount_amount(self):
        discount = self.cleaned_data.get('discount_amount', 0)
        if discount < 0:
            raise ValidationError("Discount amount cannot be negative.")
        return discount

    def clean_tax_amount(self):
        tax = self.cleaned_data.get('tax_amount', 0)
        if tax < 0:
            raise ValidationError("Tax amount cannot be negative.")
        return tax


class SaleItemForm(forms.ModelForm):
    """Enhanced SaleItem form for inline formsets."""

    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price', 'discount_percentage']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': True
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'required': True,
                'placeholder': '0.00'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            })
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_unit_price(self):
        price = self.cleaned_data.get('unit_price')
        if price <= 0:
            raise ValidationError("Unit price must be greater than zero.")
        return price

    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage', 0)
        if discount < 0 or discount > 100:
            raise ValidationError("Discount percentage must be between 0 and 100.")
        return discount

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            # Check if product has sufficient stock (placeholder for now)
            pass

        return cleaned_data


class ReturnForm(forms.ModelForm):
    """Enhanced Return form with validation."""

    class Meta:
        model = Return
        fields = [
            'sale', 'return_date', 'reason',
            'refund_amount', 'refund_method', 'employee'
        ]
        widgets = {
            'sale': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'return_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for return'
            }),
            'refund_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'required': True,
                'placeholder': '0.00'
            }),
            'refund_method': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'employee': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter sales to only show completed sales
        if 'sale' in self.fields:
            self.fields['sale'].queryset = Sale.objects.filter(
                total_amount__gt=0
            ).order_by('-sale_date')

    def clean_return_date(self):
        return_date = self.cleaned_data.get('return_date')
        if return_date and return_date > timezone.now():
            raise ValidationError("Return date cannot be in the future.")
        return return_date

    def clean_refund_amount(self):
        refund_amount = self.cleaned_data.get('refund_amount')
        sale = self.cleaned_data.get('sale')

        if refund_amount and sale and refund_amount > sale.total_amount:
            raise ValidationError(
                f"Refund amount cannot exceed the original sale amount of ${sale.total_amount}."
            )

        return refund_amount

    def clean(self):
        cleaned_data = super().clean()
        sale = cleaned_data.get('sale')
        return_date = cleaned_data.get('return_date')

        if sale and return_date:
            if return_date < sale.sale_date:
                raise ValidationError(
                    "Return date cannot be before the original sale date."
                )

        return cleaned_data


class LoyaltyTransactionForm(forms.ModelForm):
    """Enhanced Loyalty Transaction form."""

    class Meta:
        model = LoyaltyTransaction
        fields = [
            'customer', 'sale', 'points_earned',
            'points_redeemed', 'transaction_date'
        ]
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'sale': forms.Select(attrs={
                'class': 'form-control'
            }),
            'points_earned': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'points_redeemed': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'transaction_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        points_earned = cleaned_data.get('points_earned', 0)
        points_redeemed = cleaned_data.get('points_redeemed', 0)
        customer = cleaned_data.get('customer')

        # Ensure at least one type of points transaction
        if points_earned == 0 and points_redeemed == 0:
            raise ValidationError(
                "Either points earned or points redeemed must be greater than zero."
            )

        # Check if customer has sufficient points for redemption
        if customer and points_redeemed > 0:
            if customer.loyalty_points < points_redeemed:
                raise ValidationError(
                    f"Customer only has {customer.loyalty_points} loyalty points available."
                )

        return cleaned_data


# Formsets for inline forms
SaleItemFormSet = forms.inlineformset_factory(
    Sale,
    SaleItem,
    form=SaleItemForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True
)
