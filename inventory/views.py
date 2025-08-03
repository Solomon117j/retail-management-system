from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Product, Category, Brand

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'inventory/product_form.html'
    fields = ['name', 'description', 'category', 'brand', 'unit_price', 'cost_price', 'weight', 'dimensions', 'is_perishable', 'barcode']
    success_url = reverse_lazy('inventory:product_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add Bootstrap classes to form fields
        for field_name, field in form.fields.items():
            if field_name == 'is_perishable':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['category', 'brand']:
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name == 'description':
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        return form

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'inventory/product_form.html'
    fields = ['name', 'description', 'category', 'brand', 'unit_price', 'cost_price', 'weight', 'dimensions', 'is_perishable', 'barcode']
    success_url = reverse_lazy('inventory:product_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add Bootstrap classes to form fields
        for field_name, field in form.fields.items():
            if field_name == 'is_perishable':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['category', 'brand']:
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name == 'description':
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        return form

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')
