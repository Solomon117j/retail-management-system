from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.db.models import Q, F, Sum
import csv
from openpyxl import Workbook
from .models import Brand, Category, Product, InventoryRecord, StockMovement
from .forms import BrandForm, CategoryForm, ProductForm, InventoryRecordForm, StockMovementForm
from store_management.models import Store

# Brand Views
class BrandListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Brand
    template_name = 'inventory/brand_list.html'
    context_object_name = 'brands'
    permission_required = 'inventory.view_brand'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_brands'] = Brand.objects.count()
        return context

class BrandCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'inventory/brand_form.html'
    success_url = reverse_lazy('inventory:brand-list')
    permission_required = 'inventory.add_brand'

class BrandUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'inventory/brand_form.html'
    success_url = reverse_lazy('inventory:brand-list')
    permission_required = 'inventory.change_brand'

class BrandDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Brand
    template_name = 'inventory/brand_confirm_delete.html'
    success_url = reverse_lazy('inventory:brand-list')
    permission_required = 'inventory.delete_brand'

# Category Views
class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    permission_required = 'inventory.view_category'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_categories'] = Category.objects.count()
        return context

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category-list')
    permission_required = 'inventory.add_category'

class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category-list')
    permission_required = 'inventory.change_category'

class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category-list')
    permission_required = 'inventory.delete_category'

# Product Views
class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    permission_required = 'inventory.view_product'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )

        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Brand filter
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand_id=brand)

        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['active_products'] = Product.objects.filter(is_active=True).count()
        context['inactive_products'] = Product.objects.filter(is_active=False).count()
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context

class ProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'
    permission_required = 'inventory.view_product'

class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product-list')
    permission_required = 'inventory.add_product'

class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product-list')
    permission_required = 'inventory.change_product'

class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product-list')
    permission_required = 'inventory.delete_product'

# InventoryRecord Views
class InventoryRecordListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = InventoryRecord
    template_name = 'inventory/inventoryrecord_list.html'
    context_object_name = 'inventoryrecords'
    permission_required = 'inventory.view_inventoryrecord'

class InventoryRecordCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = InventoryRecord
    form_class = InventoryRecordForm
    template_name = 'inventory/inventoryrecord_form.html'
    success_url = reverse_lazy('inventory:inventoryrecord-list')
    permission_required = 'inventory.add_inventoryrecord'

class InventoryRecordUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = InventoryRecord
    form_class = InventoryRecordForm
    template_name = 'inventory/inventoryrecord_form.html'
    success_url = reverse_lazy('inventory:inventoryrecord-list')
    permission_required = 'inventory.change_inventoryrecord'

class InventoryRecordDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = InventoryRecord
    template_name = 'inventory/inventoryrecord_confirm_delete.html'
    success_url = reverse_lazy('inventory:inventoryrecord-list')
    permission_required = 'inventory.delete_inventoryrecord'

# StockMovement Views
class StockMovementListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = StockMovement
    template_name = 'inventory/stockmovement_list.html'
    context_object_name = 'stockmovements'
    permission_required = 'inventory.view_stockmovement'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('product', 'store', 'performed_by')

        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search) | Q(store__name__icontains=search)
            )

        # Store filter
        store = self.request.GET.get('store')
        if store:
            queryset = queryset.filter(store_id=store)

        # Movement type filter
        movement_type = self.request.GET.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        # Reference filter
        reference = self.request.GET.get('reference')
        if reference:
            queryset = queryset.filter(reference__icontains=reference)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_movements'] = StockMovement.objects.count()
        context['stock_in_count'] = StockMovement.objects.filter(movement_type='in').count()
        context['stock_out_count'] = StockMovement.objects.filter(movement_type='out').count()
        context['adjustments_count'] = StockMovement.objects.filter(movement_type='adjustment').count()
        context['stores'] = Store.objects.all()
        return context

class StockMovementDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = StockMovement
    template_name = 'inventory/stockmovement_detail.html'
    context_object_name = 'stockmovement'
    permission_required = 'inventory.view_stockmovement'

class StockMovementCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/stockmovement_form.html'
    success_url = reverse_lazy('inventory:stockmovement-list')
    permission_required = 'inventory.add_stockmovement'

class StockMovementUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/stockmovement_form.html'
    success_url = reverse_lazy('inventory:stockmovement-list')
    permission_required = 'inventory.change_stockmovement'

class StockMovementDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = StockMovement
    template_name = 'inventory/stockmovement_confirm_delete.html'
    success_url = reverse_lazy('inventory:stockmovement-list')
    permission_required = 'inventory.delete_stockmovement'

class InventoryDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'inventory/inventory_dashboard.html'
    permission_required = 'inventory.view_product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total products
        context['total_products'] = Product.objects.count()

        # Low stock items (quantity <= reorder_level)
        low_stock_records = InventoryRecord.objects.select_related('product').filter(
            quantity__lte=F('product__reorder_level')
        )
        context['low_stock_count'] = low_stock_records.count()
        context['low_stock_items'] = low_stock_records[:10]  # Show first 10

        # Out of stock items
        context['out_of_stock_count'] = InventoryRecord.objects.filter(quantity=0).count()

        # Recent stock movements
        context['recent_movements'] = StockMovement.objects.select_related('product').order_by('-created_at')[:10]

        # Total inventory value
        total_inventory_value = InventoryRecord.objects.aggregate(total=Sum(F('quantity') * F('cost_price')))['total'] or 0
        context['total_inventory_value'] = total_inventory_value

        return context

class StockManagementView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'inventory/stock_management.html'
    permission_required = 'inventory.view_inventoryrecord'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total inventory records
        context['total_inventory_records'] = InventoryRecord.objects.count()

        # Total stock movements
        context['total_stock_movements'] = StockMovement.objects.count()

        # Recent stock movements
        context['recent_movements'] = StockMovement.objects.select_related('product', 'store').order_by('-created_at')[:5]

        # Low stock alerts
        low_stock_records = InventoryRecord.objects.select_related('product').filter(
            quantity__lte=F('product__reorder_level')
        )
        context['low_stock_count'] = low_stock_records.count()

        # Out of stock
        context['out_of_stock_count'] = InventoryRecord.objects.filter(quantity=0).count()

        return context

@login_required
@permission_required('inventory.view_product', raise_exception=True)
def product_export(request):
    format_type = request.GET.get('format', 'csv').lower()
    queryset = Product.objects.all()

    # Apply filters
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(sku__icontains=search)
        )

    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category_id=category)

    brand = request.GET.get('brand')
    if brand:
        queryset = queryset.filter(brand_id=brand)

    status = request.GET.get('status')
    if status == 'active':
        queryset = queryset.filter(is_active=True)
    elif status == 'inactive':
        queryset = queryset.filter(is_active=False)

    if format_type == 'excel':
        # Create Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = 'Products'

        # Header
        headers = ['Name', 'SKU', 'Category', 'Brand', 'Unit Price', 'Is Active', 'Barcode', 'Weight', 'Length', 'Width', 'Height', 'Default Supplier', 'Created At']
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header)

        # Data
        for row_num, product in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=product.name)
            ws.cell(row=row_num, column=2, value=product.sku or '')
            ws.cell(row=row_num, column=3, value=product.category.name)
            ws.cell(row=row_num, column=4, value=product.brand.name)
            ws.cell(row=row_num, column=5, value=float(product.unit_price))
            ws.cell(row=row_num, column=6, value=product.is_active)
            ws.cell(row=row_num, column=7, value=product.barcode or '')
            ws.cell(row=row_num, column=8, value=float(product.weight) if product.weight else '')
            ws.cell(row=row_num, column=9, value=float(product.length) if product.length else '')
            ws.cell(row=row_num, column=10, value=float(product.width) if product.width else '')
            ws.cell(row=row_num, column=11, value=float(product.height) if product.height else '')
            ws.cell(row=row_num, column=12, value=product.default_supplier.name if product.default_supplier else '')
            ws.cell(row=row_num, column=13, value=product.created_at.strftime('%Y-%m-%d %H:%M:%S'))

        wb.save(response)
        return response

    else:  # Default to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'SKU', 'Category', 'Brand', 'Unit Price', 'Is Active', 'Barcode', 'Weight', 'Length', 'Width', 'Height', 'Default Supplier', 'Created At'])

        for product in queryset:
            writer.writerow([
                product.name,
                product.sku or '',
                product.category.name,
                product.brand.name,
                product.unit_price,
                product.is_active,
                product.barcode or '',
                product.weight or '',
                product.length or '',
                product.width or '',
                product.height or '',
                product.default_supplier.name if product.default_supplier else '',
                product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

@login_required
@permission_required('inventory.view_inventoryrecord', raise_exception=True)
def inventoryrecord_export(request):
    format_type = request.GET.get('format', 'csv').lower()
    queryset = InventoryRecord.objects.select_related('product', 'store', 'supplier', 'last_updated_by').all()

    # Apply filters
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(product__name__icontains=search) | Q(store__name__icontains=search)
        )

    product = request.GET.get('product')
    if product:
        queryset = queryset.filter(product_id=product)

    store = request.GET.get('store')
    if store:
        queryset = queryset.filter(store_id=store)

    if format_type == 'excel':
        # Create Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="inventoryrecords.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = 'Inventory Records'

        # Header
        headers = ['Product', 'Store', 'Quantity', 'Location', 'Batch Number', 'Expiration Date', 'Cost Price', 'Supplier', 'Last Updated By', 'Created At', 'Updated At']
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header)

        # Data
        for row_num, record in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=record.product.name)
            ws.cell(row=row_num, column=2, value=record.store.name)
            ws.cell(row=row_num, column=3, value=record.quantity)
            ws.cell(row=row_num, column=4, value=record.location or '')
            ws.cell(row=row_num, column=5, value=record.batch_number or '')
            ws.cell(row=row_num, column=6, value=record.expiration_date.strftime('%Y-%m-%d') if record.expiration_date else '')
            ws.cell(row=row_num, column=7, value=float(record.cost_price) if record.cost_price else '')
            ws.cell(row=row_num, column=8, value=record.supplier.name if record.supplier else '')
            ws.cell(row=row_num, column=9, value=record.last_updated_by.username if record.last_updated_by else '')
            ws.cell(row=row_num, column=10, value=record.created_at.strftime('%Y-%m-%d %H:%M:%S'))
            ws.cell(row=row_num, column=11, value=record.updated_at.strftime('%Y-%m-%d %H:%M:%S'))

        wb.save(response)
        return response

    else:  # Default to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventoryrecords.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Store', 'Quantity', 'Location', 'Batch Number', 'Expiration Date', 'Cost Price', 'Supplier', 'Last Updated By', 'Created At', 'Updated At'])

        for record in queryset:
            writer.writerow([
                record.product.name,
                record.store.name,
                record.quantity,
                record.location or '',
                record.batch_number or '',
                record.expiration_date.strftime('%Y-%m-%d') if record.expiration_date else '',
                record.cost_price or '',
                record.supplier.name if record.supplier else '',
                record.last_updated_by.username if record.last_updated_by else '',
                record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                record.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

@login_required
@permission_required('inventory.view_stockmovement', raise_exception=True)
def stockmovement_export(request):
    format_type = request.GET.get('format', 'csv').lower()
    queryset = StockMovement.objects.select_related('product', 'store', 'performed_by').all()

    # Apply filters
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(product__name__icontains=search) | Q(store__name__icontains=search)
        )

    product = request.GET.get('product')
    if product:
        queryset = queryset.filter(product_id=product)

    store = request.GET.get('store')
    if store:
        queryset = queryset.filter(store_id=store)

    movement_type = request.GET.get('movement_type')
    if movement_type:
        queryset = queryset.filter(movement_type=movement_type)

    if format_type == 'excel':
        # Create Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="stockmovements.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = 'Stock Movements'

        # Header
        headers = ['Product', 'Store', 'Quantity', 'Movement Type', 'Reason', 'Reference', 'Performed By', 'Created At']
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header)

        # Data
        for row_num, movement in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=movement.product.name)
            ws.cell(row=row_num, column=2, value=movement.store.name)
            ws.cell(row=row_num, column=3, value=movement.quantity)
            ws.cell(row=row_num, column=4, value=movement.get_movement_type_display())
            ws.cell(row=row_num, column=5, value=movement.get_reason_display() if movement.reason else '')
            ws.cell(row=row_num, column=6, value=movement.reference or '')
            ws.cell(row=row_num, column=7, value=movement.performed_by.username if movement.performed_by else '')
            ws.cell(row=row_num, column=8, value=movement.created_at.strftime('%Y-%m-%d %H:%M:%S'))

        wb.save(response)
        return response

    else:  # Default to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stockmovements.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Store', 'Quantity', 'Movement Type', 'Reason', 'Reference', 'Performed By', 'Created At'])

        for movement in queryset:
            writer.writerow([
                movement.product.name,
                movement.store.name,
                movement.quantity,
                movement.get_movement_type_display(),
                movement.get_reason_display() if movement.reason else '',
                movement.reference or '',
                movement.performed_by.username if movement.performed_by else '',
                movement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

@login_required
@permission_required('inventory.view_brand', raise_exception=True)
def brand_export(request):
    format_type = request.GET.get('format', 'csv').lower()
    queryset = Brand.objects.all()

    # Apply filters if any (similar to product_export)
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(name__icontains=search)

    if format_type == 'excel':
        # Create Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="brands.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = 'Brands'

        # Header
        headers = ['Name', 'Description', 'Products Count', 'Created At']
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header)

        # Data
        for row_num, brand in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=brand.name)
            ws.cell(row=row_num, column=2, value=brand.description or '')
            ws.cell(row=row_num, column=3, value=brand.products.count())
            ws.cell(row=row_num, column=4, value=brand.created_at.strftime('%Y-%m-%d %H:%M:%S'))

        wb.save(response)
        return response

    else:  # Default to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="brands.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Description', 'Products Count', 'Created At'])

        for brand in queryset:
            writer.writerow([
                brand.name,
                brand.description or '',
                brand.products.count(),
                brand.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

@login_required
@permission_required('inventory.view_category', raise_exception=True)
def category_export(request):
    format_type = request.GET.get('format', 'csv').lower()
    queryset = Category.objects.all()

    # Apply filters if any
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(name__icontains=search)

    if format_type == 'excel':
        # Create Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="categories.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = 'Categories'

        # Header
        headers = ['Name', 'Description', 'Products Count', 'Created At']
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header)

        # Data
        for row_num, category in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=category.name)
            ws.cell(row=row_num, column=2, value=category.description or '')
            ws.cell(row=row_num, column=3, value=category.products.count())
            ws.cell(row=row_num, column=4, value=category.created_at.strftime('%Y-%m-%d %H:%M:%S'))

        wb.save(response)
        return response

    else:  # Default to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="categories.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Description', 'Products Count', 'Created At'])

        for category in queryset:
            writer.writerow([
                category.name,
                category.description or '',
                category.products.count(),
                category.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

@login_required
@permission_required('inventory.change_product', raise_exception=True)
def push_to_ecommerce(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        if product_ids:
            products = Product.objects.filter(id__in=product_ids)
            updated_count = products.update(show_online=True)
            messages.success(request, f'Successfully pushed {updated_count} products to e-commerce.')
        else:
            messages.warning(request, 'No products selected.')
        return redirect('inventory:product-list')
    return redirect('inventory:product-list')
