# ecommerce/urls.py
from django.urls import path
from . import views 
from .views import CustomerAccountListView, CustomerAccountDetailView


app_name = 'e_commerce'

from django.urls import path
from .views import (
    CustomerAccountListView,
    CustomerAccountDetailView,
    OnlineOrderListView,
    OnlineOrderCreateView,
    OnlineOrderDetailView,
    OnlineOrderUpdateView,
    OnlineOrderDeleteView,
    OnlineOrderStatusUpdateView,
    ProductBrowseView,
    ProductDetailView,
    AddToCartView,
    CartView,
    RemoveFromCartView,
    CheckoutView,
    OrderExportView,
)

urlpatterns = [
    path('orders/', OnlineOrderListView.as_view(), name='online_order_list'),
    path('orders/create/', OnlineOrderCreateView.as_view(), name='order_create'),
    path('orders/<uuid:pk>/', OnlineOrderDetailView.as_view(), name='order_detail'),
    path('orders/<uuid:pk>/update/', OnlineOrderUpdateView.as_view(), name='order_update'),
    path('orders/<uuid:pk>/delete/', OnlineOrderDeleteView.as_view(), name='order_delete'),
    path('orders/<uuid:pk>/status/', OnlineOrderStatusUpdateView.as_view(), name='order_status'),
    path('customer-accounts/', CustomerAccountListView.as_view(), name='customer_account_list'),
    path('customer-accounts/<uuid:pk>/', CustomerAccountDetailView.as_view(), name='customer_account_detail'),

    # Product browsing page for customers
    path('products/', ProductBrowseView.as_view(), name='product_browse'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Cart functionality
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # Data export
    path('orders/export/', OrderExportView.as_view(), name='order_export'),
]
