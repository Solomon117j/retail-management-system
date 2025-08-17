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
]