from django import forms
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
# from .models import Store, Department
from django.shortcuts import get_object_or_404
from store_management.models import Store , Department 

from django.views.generic import TemplateView



from .forms import DepartmentForm, StoreForm

from .forms import Department

import logging

logger = logging.getLogger(__name__)

# Store Views



def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('store_management:department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'departments/edit.html', {
        'form': form,
        'department': department
    })

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
        # Ensure we're getting a valid queryset with PKs
        context['departments'] = self.object.departments.all().order_by('department_name')
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
    success_url = reverse_lazy('store_management:store_list')



class StoreDeleteView(DeleteView):
    model = Store
    template_name = 'store_management/store_confirm_delete.html'
    success_url = reverse_lazy('store_management:store_list')

# Department Views
# store_management/views.py
# views.py
from django.shortcuts import get_object_or_404

class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    
    def form_valid(self, form):
        # Use id instead of store_id
        store = get_object_or_404(Store, id=self.kwargs['store_id'])
        form.instance.store = store
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use id here too
        context['store'] = get_object_or_404(Store, id=self.kwargs['store_id'])
        return context
    
    def get_success_url(self):
        return reverse('store_management:department_list', kwargs={
            'store_id': self.kwargs['store_id']
        })
# views.py
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'store_management/department_edit.html'
    context_object_name = 'department'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add store to context
        context['store'] = self.object.store
        return context
    
    def get_success_url(self):
        return reverse('store_management:department_list', kwargs={
            'store_id': self.object.store.id
        })
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'store_management/department_confirm_delete.html'

    def get_success_url(self):
        # Use store_id from department's foreign key
        return reverse_lazy('store_management:department_list', kwargs={'store_id': self.object.store.id})


class DepartmentListView(ListView):
    model = Department
    context_object_name = 'departments'
    template_name = 'store_management/department_list.html'

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        # Use store_id field directly
        return Department.objects.filter(store_id=store_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs['store_id']
        # Use id field instead of store_id
        context['store'] = get_object_or_404(Store, id=store_id)
        return context
#

class DepartmentDetailView(DetailView):
    model = Department
    template_name = 'store_management/department_detail.html'  # Your template path
    context_object_name = 'department'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add store to context from the department's foreign key
        context['store'] = self.object.store
        return context