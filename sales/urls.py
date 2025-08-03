from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Customer URLs
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/update/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    
    # Sale URLs
    path('sales/', views.SaleListView.as_view(), name='sale_list'),
    path('sales/create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('sales/<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sales/<int:pk>/update/', views.SaleUpdateView.as_view(), name='sale_update'),
    path('sales/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),
    
    # Return URLs
    path('returns/create/', views.ReturnCreateView.as_view(), name='return_create'),
    path('returns/<int:pk>/update/', views.ReturnUpdateView.as_view(), name='return_update'),
    path('returns/<int:pk>/delete/', views.ReturnDeleteView.as_view(), name='return_delete'),
    
    # Loyalty Transaction URLs
    path('loyalty/create/', views.LoyaltyTransactionCreateView.as_view(), name='loyaltytransaction_create'),
    path('loyalty/<int:pk>/update/', views.LoyaltyTransactionUpdateView.as_view(), name='loyaltytransaction_update'),
    path('loyalty/<int:pk>/delete/', views.LoyaltyTransactionDeleteView.as_view(), name='loyaltytransaction_delete'),
]