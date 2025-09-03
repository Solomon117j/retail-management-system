# inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Products
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Stock
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/adjust/', views.StockAdjustmentCreateView.as_view(), name='stock_adjust'),
    path('stock/movements/', views.StockMovementListView.as_view(), name='stock_movement_list'),

    # Brands
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brand/create/', views.BrandCreateView.as_view(), name='brand_create'),
    path('brand/<int:pk>/edit/', views.BrandUpdateView.as_view(), name='brand_edit'),
    path('brand/<int:pk>/delete/', views.BrandDeleteView.as_view(), name='brand_delete'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Store Inventory
    path('store-inventory/', views.StoreInventoryListView.as_view(), name='storeinventory_list'),
]