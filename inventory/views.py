from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum

from .models import Product, StoreInventory, StockMovement, Brand, Category
from .forms import ProductForm, StockAdjustmentForm


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
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')


class StockListView(LoginRequiredMixin, ListView):
    model = StoreInventory
    template_name = 'inventory/stock_list.html'
    context_object_name = 'stocks'
    paginate_by = 25

    def get_queryset(self):
        qs = StoreInventory.objects.select_related('product', 'store')
        store_id = self.request.GET.get('store')
        product_name = self.request.GET.get('q')
        if store_id:
            qs = qs.filter(store_id=store_id)
        if product_name:
            qs = qs.filter(product__name__icontains=product_name)
        return qs.order_by('store__name', 'product__name')

    def get_context_data(self, **kwargs):
        from store_management.models import Store
        ctx = super().get_context_data(**kwargs)
        ctx['stores'] = Store.objects.all()
        # totals per store
        ctx['totals'] = StoreInventory.objects.values('store__name').annotate(total=Sum('quantity'))
        return ctx


class StockAdjustmentCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockAdjustmentForm
    template_name = 'inventory/stock_adjust_form.html'
    success_url = reverse_lazy('inventory:stock_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        messages.success(self.request, 'Stock adjusted successfully.')
        return super().form_valid(form)


class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'inventory/stock_movement_list.html'
    context_object_name = 'movements'
    paginate_by = 25

    def get_queryset(self):
        qs = StockMovement.objects.select_related('product', 'store', 'created_by')
        store_id = self.request.GET.get('store')
        product_id = self.request.GET.get('product')
        if store_id:
            qs = qs.filter(store_id=store_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

class BrandListView(ListView):
    model = Brand
    template_name = 'inventory/brand_list.html'


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'


class StoreInventoryListView(LoginRequiredMixin, ListView):
    model = StoreInventory
    template_name = 'inventory/storeinventory_list.html'
    context_object_name = 'store_inventories'