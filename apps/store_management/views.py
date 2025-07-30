from django import forms
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Store, Department
from django.shortcuts import get_object_or_404

# Store Views

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
        widgets = {
            'opening_date': forms.DateInput(attrs={'type': 'date'})
        }
class StoreListView(ListView):
    model = Store
    context_object_name = 'stores'
    template_name = 'store_management/store_list.html'

class StoreDetailView(DetailView):
    model = Store
    context_object_name = 'store'
    template_name = 'store_management/store_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store = self.get_object()
        context['departments'] = store.departments.all()
        return context

class StoreCreateView(CreateView):
    form_class = StoreForm  # Use custom form instead of fields
    template_name = 'store_management/store_form.html'
    success_url = reverse_lazy('store_management:store_list')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            # Add error to form for display
            form.add_error(None, f"Save error: {str(e)}")
            return self.form_invalid(form)

class StoreUpdateView(UpdateView):
    model = Store
    fields = [
        'store_name', 'address', 'city', 
        'region', 'postal_code', 'phone', 'opening_date'
    ]
    template_name = 'store_management/store_form.html'
    success_url = reverse_lazy('store_list')

class StoreDeleteView(DeleteView):
    model = Store
    template_name = 'store_management/store_confirm_delete.html'
    success_url = reverse_lazy('store_list')

# Department Views
# store_management/views.py
class DepartmentCreateView(CreateView):
    model = Department
    fields = ['department_name', 'description']
    template_name = 'store_management/department_form.html'

    def form_valid(self, form):
        form.instance.store = get_object_or_404(Store, pk=self.kwargs['store_id'])
        response = super().form_valid(form)
        if not self.object.pk:
            form.add_error(None, 'Failed to create department - no primary key assigned')
            return self.form_invalid(form)
        return response

    def get_success_url(self):
        return reverse_lazy('store_management:department_list', args=[self.object.store.store_id])

class DepartmentUpdateView(UpdateView):
    model = Department
    fields = ['department_name', 'description']
    template_name = 'store_management/department_form.html'
    
    def get_success_url(self):
        return reverse_lazy('department_list', args=[self.object.store.store_id])

class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'store_management/department_confirm_delete.html'
    
    def get_success_url(self):
        store_id = self.object.store.store_id
        return reverse_lazy('department_list', args=[store_id])

class DepartmentListView(ListView):
    model = Department
    context_object_name = 'departments'
    template_name = 'store_management/department_list.html'
    
    def get_queryset(self):
        store_id = self.kwargs['store_id']
        return Department.objects.filter(store__store_id=store_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = Store.objects.get(pk=self.kwargs['store_id'])
        return context
# Create your views here.
