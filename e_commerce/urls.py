# ecommerce/urls.py
from django.urls import path
from . import views 
from .views import CustomerAccountListView, CustomerAccountDetailView


app_name = 'e_commerce'

urlpatterns = [
    path('orders/', views.OnlineOrderListView.as_view(), name='online_order_list'),
    path('orders/create/', views.OnlineOrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OnlineOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update/', views.OnlineOrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', views.OnlineOrderDeleteView.as_view(), name='order_delete'),
    path('orders/<int:pk>/status/', views.OnlineOrderStatusUpdateView.as_view(), name='order_status'),
    path('customer-accounts/', CustomerAccountListView.as_view(), name='customer_account_list'),
    path('customer-accounts/<int:pk>/', CustomerAccountDetailView.as_view(), name='customer_account_detail'),

    # Customer Account URLs
    # path('customers/', views.CustomerAccountListView.as_view(), name='customer_account_list'),
]