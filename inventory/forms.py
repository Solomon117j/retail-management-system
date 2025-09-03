from django import forms
from .models import Product, Category, Brand, StockMovement, StoreInventory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'brand', 'unit_price', 'cost_price', 
                 'weight', 'dimensions', 'available_online', 'image', 'is_perishable', 'barcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'available_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_perishable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure we have categories and brands available
        if not Category.objects.exists():
            # Create a default category if none exist
            Category.objects.create(name="General", description="General category for products")
        
        if not Brand.objects.exists():
            # Create a default brand if none exist
            Brand.objects.create(name="Generic", description="Generic brand for products")
            
        # Refresh the querysets
        self.fields['category'].queryset = Category.objects.all()
        self.fields['brand'].queryset = Brand.objects.all()
        
        # Add empty option for brand (since it's optional)
        self.fields['brand'].empty_label = "Select a brand (optional)"
        
    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')
        if barcode:
            # Check if barcode already exists (excluding current instance if editing)
            existing = Product.objects.filter(barcode=barcode)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("A product with this barcode already exists.")
        return barcode


class StockAdjustmentForm(forms.ModelForm):
    """Form for manual stock adjustments; quantity is a signed delta."""
    class Meta:
        model = StockMovement
        fields = ['product', 'store', 'quantity', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'store': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.movement_type = StockMovement.MOVEMENT_ADJUST
        if commit:
            obj.save()  # triggers apply()
        return obj


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make parent optional
        self.fields['parent'].required = False
        self.fields['description'].required = False
        # Add empty label for parent dropdown
        self.fields['parent'].empty_label = "Select parent category (optional)"

        # Filter out self from parent options when editing
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make description and website optional
        self.fields['description'].required = False
        self.fields['website'].required = False


class StoreInventoryForm(forms.ModelForm):
    class Meta:
        model = StoreInventory
        fields = ['product', 'store', 'quantity', 'reorder_level', 'aisle_location']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'store': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'required': True, 'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'aisle_location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make aisle_location optional
        self.fields['aisle_location'].required = False
        # Set default reorder level
        if not self.instance.pk:
            self.fields['reorder_level'].initial = 10

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity

    def clean_reorder_level(self):
        reorder_level = self.cleaned_data.get('reorder_level')
        if reorder_level < 0:
            raise forms.ValidationError("Reorder level cannot be negative.")
        return reorder_level


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'store', 'movement_type', 'quantity', 'reference', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'store': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'movement_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make reference and note optional
        self.fields['reference'].required = False
        self.fields['note'].required = False

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        movement_type = self.cleaned_data.get('movement_type')

        if quantity <= 0:
            raise forms.ValidationError("Quantity must be positive.")

        # For adjustment, allow negative values
        if movement_type == StockMovement.MOVEMENT_ADJUST and quantity > 0:
            # This is fine, adjustment can be positive or negative
            pass

        return quantity
