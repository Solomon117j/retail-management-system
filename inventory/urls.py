from django.urls import path
from .views import (
    BrandListView, BrandCreateView, BrandUpdateView, BrandDeleteView, brand_export,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView, category_export,
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView, product_export,
    InventoryRecordListView, InventoryRecordCreateView, InventoryRecordUpdateView, InventoryRecordDeleteView, inventoryrecord_export,
    StockMovementListView, StockMovementDetailView, StockMovementCreateView, StockMovementUpdateView, StockMovementDeleteView, stockmovement_export,
    InventoryDashboardView,
    StockManagementView,
    push_to_ecommerce,
)

app_name = 'inventory'

urlpatterns = [
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/add/', BrandCreateView.as_view(), name='brand-add'),
    path('brands/<int:pk>/edit/', BrandUpdateView.as_view(), name='brand-edit'),
    path('brands/<int:pk>/delete/', BrandDeleteView.as_view(), name='brand-delete'),
    path('brands/export/', brand_export, name='brand_export'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('categories/export/', category_export, name='category_export'),

    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/add/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('products/export/', product_export, name='product_export'),

    path('inventoryrecords/', InventoryRecordListView.as_view(), name='inventoryrecord-list'),
    path('inventoryrecords/add/', InventoryRecordCreateView.as_view(), name='inventoryrecord_create'),
    path('inventoryrecords/<int:pk>/edit/', InventoryRecordUpdateView.as_view(), name='inventoryrecord_update'),
    path('inventoryrecords/<int:pk>/delete/', InventoryRecordDeleteView.as_view(), name='inventoryrecord_delete'),
    path('inventoryrecords/export/', inventoryrecord_export, name='inventoryrecord_export'),

    path('stockmovements/', StockMovementListView.as_view(), name='stockmovement-list'),
    path('stockmovements/<int:pk>/', StockMovementDetailView.as_view(), name='stockmovement_detail'),
    path('stockmovements/add/', StockMovementCreateView.as_view(), name='stockmovement_create'),
    path('stockmovements/<int:pk>/edit/', StockMovementUpdateView.as_view(), name='stockmovement_update'),
    path('stockmovements/<int:pk>/delete/', StockMovementDeleteView.as_view(), name='stockmovement_delete'),
    path('stockmovements/export/', stockmovement_export, name='stockmovement_export'),

    path('dashboard/', InventoryDashboardView.as_view(), name='inventory-dashboard'),
    path('stock-management/', StockManagementView.as_view(), name='stock-management'),
    path('products/push-to-ecommerce/', push_to_ecommerce, name='push_to_ecommerce'),
]
