# ecommerce/urls.py
from django.urls import path
from . import views

app_name = 'e_commerce'

urlpatterns = [
    # Online Order URLs
    path('orders/', views.OnlineOrderListView.as_view(), name='order_list'),
    path('orders/create/', views.OnlineOrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OnlineOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update/', views.OnlineOrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', views.OnlineOrderDeleteView.as_view(), name='order_delete'),
    path('orders/<int:pk>/status/', views.OnlineOrderStatusUpdateView.as_view(), name='order_status'),
]