# store_management/forms.py
from django import forms
from .models import Department, Store

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'description']  # Add your actual fields
        
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
        widgets = {
            'opening_date': forms.DateInput(attrs={'type': 'date'})
        }