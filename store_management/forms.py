# store_management/forms.py
from django import forms
from .models import Department, Store
from human_resources.models import Employee


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
    country_code = forms.CharField(
        max_length=5,
        initial='+268',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+268'
        }),
        help_text='Country code (e.g., +268 for Eswatini)'
    )

    class Meta:
        model = Store
        fields = ['store_name', 'address', 'city', 'region', 'postal_code', 'phone', 'opening_date', 'manager']
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
                'placeholder': '78117803',
                'maxlength': 20
            }),
            'opening_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

        help_texts = {
            'store_name': 'Enter a unique name for this store location',
            'address': 'Full street address including building number',
            'city': 'City where the store is located',
            'region': 'State, province, or region',
            'postal_code': 'ZIP code or postal code (optional)',
            'phone': 'Local phone number (without country code, e.g., 78117803)',
            'opening_date': 'Date when the store first opened',
            'manager': 'Select the store manager from the list of employees (optional)'
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

        # Set postal_code as optional
        self.fields['postal_code'].required = False

        # Set manager as optional and set queryset
        self.fields['manager'].required = False
        self.fields['manager'].queryset = Employee.objects.all().order_by('first_name', 'last_name')

        # If editing existing instance, split phone into country code and local number
        if self.instance and self.instance.pk and self.instance.phone:
            phone_str = str(self.instance.phone)
            if len(phone_str) == 11:
                self.fields['country_code'].initial = '+268'  # Assuming +268 for existing
                self.fields['phone'].initial = phone_str[3:]  # Remove first 3 digits (268)

    def clean_phone(self):
        """Validate phone number: require 11 digits, return digits only"""
        phone = self.cleaned_data.get('phone')
        country_code = self.cleaned_data.get('country_code')
        if phone and country_code:
            # Remove all non-digit characters from phone and country code
            digits_only_phone = ''.join(filter(str.isdigit, phone))
            digits_only_code = ''.join(filter(str.isdigit, country_code))

            # Combine country code digits and phone digits
            full_number = digits_only_code + digits_only_phone

            # Require exactly 11 digits total (e.g., 26878117803)
            if len(full_number) != 11:
                raise forms.ValidationError(
                    'Full phone number including country code must be 11 digits long (e.g., +268 78117803)'
                )

            # Store normalized digits-only value (just phone part)
            return digits_only_phone

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
