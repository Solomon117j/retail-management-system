from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    # Supplier URLs
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # HTMX Supplier Endpoints
    path('suppliers/<int:pk>/edit-form/', views.supplier_edit_form, name='supplier_edit_form'),
    path('suppliers/htmx-save/', views.supplier_htmx_save, name='supplier_htmx_save'),
    
    # Supplier Product URLs
    path('suppliers/<int:supplier_id>/products/add/', 
         views.SupplierProductCreateView.as_view(), name='supplierproduct_create'),
    path('supplier-products/<int:pk>/update/', 
         views.SupplierProductUpdateView.as_view(), name='supplierproduct_update'),
    path('supplier-products/<int:pk>/delete/', 
         views.SupplierProductDeleteView.as_view(), name='supplierproduct_delete'),
    
    # Purchase Order URLs
    path('orders/', views.PurchaseOrderListView.as_view(), name='purchaseorder_list'),
    path('orders/create/', views.PurchaseOrderCreateView.as_view(), name='purchaseorder_create'),
    path('orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchaseorder_detail'),
    path('orders/<int:pk>/update/', views.PurchaseOrderUpdateView.as_view(), name='purchaseorder_update'),
    path('orders/<int:pk>/delete/', views.PurchaseOrderDeleteView.as_view(), name='purchaseorder_delete'),
    path('orders/<int:pk>/status/', views.PurchaseOrderStatusUpdateView.as_view(), name='purchaseorder_status'),
    path('orders/<int:pk>/receive/', views.PurchaseOrderReceiveView.as_view(), name='purchaseorder_receive'),
]