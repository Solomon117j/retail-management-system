# procurement/forms.py
import datetime
from django import forms
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, SupplierProduct
from inventory.models import Product


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'email', 'phone', 'address',
            'contract_start_date', 'payment_terms', 'is_active',
            'website', 'tax_id', 'industry', 'notes',
            'api_endpoint', 'api_key', 'on_time_delivery_rate',
            'quality_rating', 'total_orders', 'total_spent',
            'compliance_score', 'tenant_id'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name',
                'maxlength': 100
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name',
                'maxlength': 100
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'supplier@example.com',
                'maxlength': 100
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'maxlength': 20
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter full address',
                'maxlength': 200
            }),
            'contract_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'payment_terms': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Net 30 days',
                'maxlength': 100
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.supplierwebsite.com',
                'maxlength': 200
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tax ID',
                'maxlength': 50
            }),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Retail, Manufacturing',
                'maxlength': 100
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional notes about the supplier'
            }),
            'api_endpoint': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://api.supplier.com',
                'maxlength': 200
            }),
            'api_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter API key',
                'maxlength': 255
            }),
            'on_time_delivery_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'quality_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.0',
                'step': '0.1',
                'min': '0',
                'max': '5'
            }),
            'total_orders': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'total_spent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'compliance_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'tenant_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tenant ID',
                'maxlength': 50
            }),
        }

        help_texts = {
            'name': 'Enter a unique name for this supplier',
            'contact_person': 'Primary contact person at the supplier',
            'email': 'Supplier email address for communications',
            'phone': 'Supplier phone number',
            'address': 'Full address of the supplier',
            'contract_start_date': 'Date when the contract with this supplier started',
            'payment_terms': 'Payment terms agreed with the supplier',
            'is_active': 'Check if the supplier is currently active',
            'website': 'Supplier\'s official website URL',
            'tax_id': 'Supplier\'s tax identification number',
            'industry': 'Industry or sector the supplier operates in',
            'notes': 'Any additional information about the supplier',
            'api_endpoint': 'API endpoint for third-party integrations',
            'api_key': 'API key for authentication with the supplier\'s system',
            'on_time_delivery_rate': 'Percentage of on-time deliveries (0-100)',
            'quality_rating': 'Quality rating out of 5 (0-5)',
            'total_orders': 'Total number of orders placed with this supplier',
            'total_spent': 'Total amount spent with this supplier',
            'compliance_score': 'Compliance score percentage (0-100)',
            'tenant_id': 'Tenant ID for multi-tenant architecture'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['address'].required = True

    def clean_on_time_delivery_rate(self):
        rate = self.cleaned_data.get('on_time_delivery_rate')
        if rate is not None and (rate < 0 or rate > 100):
            raise forms.ValidationError('On-time delivery rate must be between 0 and 100')
        return rate

    def clean_quality_rating(self):
        rating = self.cleaned_data.get('quality_rating')
        if rating is not None and (rating < 0 or rating > 5):
            raise forms.ValidationError('Quality rating must be between 0 and 5')
        return rating

    def clean_compliance_score(self):
        score = self.cleaned_data.get('compliance_score')
        if score is not None and (score < 0 or score > 100):
            raise forms.ValidationError('Compliance score must be between 0 and 100')
        return score


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'store', 'expected_delivery_date']
        widgets = {
            'supplier': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'data-bs-toggle': 'tooltip',
                'title': 'Select the supplier for this order'
            }),
            'store': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'data-bs-toggle': 'tooltip',
                'title': 'Select the store receiving the order'
            }),
            'expected_delivery_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-lg',
                'min': '{{ today|date:"Y-m-d" }}',
                'data-bs-toggle': 'tooltip',
                'title': 'Expected delivery date (must be in the future)'
            }),
        }
        labels = {
            'supplier': 'Supplier',
            'store': 'Destination Store',
            'expected_delivery_date': 'Expected Delivery Date',
        }
        help_texts = {
            'supplier': 'Choose a registered supplier from the list.',
            'store': 'Select the store location that will receive the goods.',
            'expected_delivery_date': 'Set a realistic delivery date based on supplier lead time.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].required = True
        self.fields['store'].required = True
        self.fields['expected_delivery_date'].required = True
        # Add Bootstrap validation classes
        for field in self.fields:
            if isinstance(self.fields[field].widget, forms.Select):
                self.fields[field].widget.attrs.setdefault('class', '')
                self.fields[field].widget.attrs['class'] += ' border-primary'
            else:
                self.fields[field].widget.attrs.setdefault('class', '')
                self.fields[field].widget.attrs['class'] += ' border-primary'

    def clean_expected_delivery_date(self):
        delivery_date = self.cleaned_data.get('expected_delivery_date')
        if delivery_date and delivery_date < datetime.date.today():
            raise forms.ValidationError('Expected delivery date cannot be in the past.')
        return delivery_date


class SupplierProductForm(forms.ModelForm):
    class Meta:
        model = SupplierProduct
        fields = ['product', 'supply_price', 'lead_time', 'minimum_order_quantity']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'data-bs-toggle': 'tooltip',
                'title': 'Select the product from inventory'
            }),
            'supply_price': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'data-bs-toggle': 'tooltip',
                'title': 'Enter the supply price per unit'
            }),
            'lead_time': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'min': '0',
                'step': '1',
                'placeholder': '0',
                'data-bs-toggle': 'tooltip',
                'title': 'Lead time in days (optional)'
            }),
            'minimum_order_quantity': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'min': '1',
                'step': '1',
                'placeholder': '1',
                'data-bs-toggle': 'tooltip',
                'title': 'Minimum quantity that can be ordered'
            }),
        }
        labels = {
            'product': 'Product',
            'supply_price': 'Supply Price (SZL)',
            'lead_time': 'Lead Time (days)',
            'minimum_order_quantity': 'Minimum Order Quantity',
        }
        help_texts = {
            'product': 'Select the product this supplier provides.',
            'supply_price': 'The price per unit charged by this supplier.',
            'lead_time': 'Number of days required to deliver after order placement.',
            'minimum_order_quantity': 'The smallest quantity that can be ordered from this supplier.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all().order_by('name')
        # Make certain fields required
        self.fields['product'].required = True
        self.fields['supply_price'].required = True
        self.fields['minimum_order_quantity'].required = True
        # Add Bootstrap validation classes
        for field in self.fields:
            if isinstance(self.fields[field].widget, forms.Select):
                self.fields[field].widget.attrs.setdefault('class', '')
                self.fields[field].widget.attrs['class'] += ' border-primary'
            else:
                self.fields[field].widget.attrs.setdefault('class', '')
                self.fields[field].widget.attrs['class'] += ' border-primary'

    def clean_supply_price(self):
        price = self.cleaned_data.get('supply_price')
        if price is not None and price <= 0:
            raise forms.ValidationError('Supply price must be greater than 0')
        return price

    def clean_minimum_order_quantity(self):
        quantity = self.cleaned_data.get('minimum_order_quantity')
        if quantity is not None and quantity < 1:
            raise forms.ValidationError('Minimum order quantity must be at least 1')
        return quantity

    def clean_lead_time(self):
        lead_time = self.cleaned_data.get('lead_time')
        if lead_time is not None and lead_time < 0:
            raise forms.ValidationError('Lead time cannot be negative')
        return lead_time


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select',
                'data-bs-toggle': 'tooltip',
                'title': 'Select a product from inventory'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity',
                'min': '1',
                'step': '1',
                'placeholder': 'Qty',
                'data-bs-toggle': 'tooltip',
                'title': 'Enter the quantity to order'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control unit-price',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'data-bs-toggle': 'tooltip',
                'title': 'Enter unit price in SZL'
            }),
        }
        labels = {
            'product': 'Product',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price (SZL)',
        }
        help_texts = {
            'product': 'Choose from available products.',
            'quantity': 'Minimum order quantity applies.',
            'unit_price': 'Price per unit from supplier catalog.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all().order_by('name')
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' shadow-sm'
