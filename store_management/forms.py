# store_management/forms.py
from django import forms
from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager']  # Add your actual fields
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add customizations here (e.g., set querysets)
        self.fields['manager'].queryset = self.instance.store.employees.all()