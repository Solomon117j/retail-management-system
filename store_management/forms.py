# store_management/forms.py
from django import forms
from .models import Department, Store


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'description']
        widgets = {
            'department_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter department description (optional)'
            })
        }


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
        widgets = {
            'store_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter store name',
                'maxlength': 100
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full street address',
                'maxlength': 200
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city name',
                'maxlength': 50
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state/province/region',
                'maxlength': 50
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter postal/ZIP code',
                'maxlength': 20
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567',
                'maxlength': 20
            }),
            'opening_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        
        help_texts = {
            'store_name': 'Enter a unique name for this store location',
            'address': 'Full street address including building number',
            'city': 'City where the store is located',
            'region': 'State, province, or region',
            'postal_code': 'ZIP code or postal code (optional)',
            'phone': 'Main contact phone number for the store',
            'opening_date': 'Date when the store first opened',
            'manager': 'Select the store manager (optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make certain fields required
        self.fields['store_name'].required = True
        self.fields['address'].required = True
        self.fields['city'].required = True
        self.fields['region'].required = True
        self.fields['phone'].required = True
        self.fields['opening_date'].required = True
        
        # Set postal_code and manager as optional
        self.fields['postal_code'].required = False
        self.fields['manager'].required = False
        
        # Add empty label for manager dropdown
        self.fields['manager'].empty_label = "Select a manager (optional)"
    
    def clean_phone(self):
        """Validate and format phone number"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters
            digits_only = ''.join(filter(str.isdigit, phone))
            
            # Check if it's a valid length (10 digits for US format)
            if len(digits_only) != 10:
                raise forms.ValidationError(
                    'Phone number must be 10 digits long (e.g., 555-123-4567)'
                )
            
            # Format as (XXX) XXX-XXXX
            formatted_phone = f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
            return formatted_phone
        
        return phone
    
    def clean_postal_code(self):
        """Validate postal code format"""
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            # Convert to uppercase and remove spaces
            postal_code = postal_code.upper().replace(' ', '')
            
            # Basic validation (can be extended for specific country formats)
            if len(postal_code) < 3 or len(postal_code) > 10:
                raise forms.ValidationError(
                    'Postal code must be between 3 and 10 characters'
                )
        
        return postal_code