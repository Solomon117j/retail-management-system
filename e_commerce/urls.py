from django.urls import path
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .views import (
    CustomerAccountListView,
    CustomerAccountDetailView,
    CustomerAccountUpdateView,
    OnlineOrderListView,
    OnlineOrderCreateView,
    OnlineOrderUpdateView,
    OnlineOrderDetailView,
    OnlineOrderStatusUpdateView,
    OnlineOrderDeleteView,
    ProductBrowseView,
    ProductDetailView,
    AddToCartView,
    CartView,
    RemoveFromCartView,
    CheckoutView,
    OrderExportView,
    checkout_success,
    PayFastNotifyView,
    MTNMoMoVerifyView,
    MyGateWebhookView,
)

app_name = 'e_commerce'

urlpatterns = [
    # Customer Account URLs
    path('customer-accounts/', CustomerAccountListView.as_view(), name='customer_account_list'),
    path('customer-accounts/<uuid:pk>/', CustomerAccountDetailView.as_view(), name='customer_account_detail'),
    path('customer-accounts/<uuid:pk>/update/', CustomerAccountUpdateView.as_view(), name='customer_account_update'),

    # Password Change URLs
    path('password_change/', PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),

    # Online Order URLs
    path('orders/', OnlineOrderListView.as_view(), name='online_order_list'),
    path('orders/create/', OnlineOrderCreateView.as_view(), name='online_order_create'),
    path('orders/<int:pk>/', OnlineOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update/', OnlineOrderUpdateView.as_view(), name='online_order_update'),
    path('orders/<int:pk>/status/', OnlineOrderStatusUpdateView.as_view(), name='online_order_status_update'),
    path('orders/<int:pk>/delete/', OnlineOrderDeleteView.as_view(), name='online_order_delete'),

    # Product URLs
    path('products/', ProductBrowseView.as_view(), name='product_browse'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Cart URLs
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),

    # Checkout URLs
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/success/', checkout_success, name='checkout_success'),

    # Payment Webhook URLs
    path('payfast/notify/', PayFastNotifyView.as_view(), name='payfast_notify'),
    path('mtn-momo/verify/', MTNMoMoVerifyView.as_view(), name='mtn_momo_verify'),
    path('mygate/webhook/', MyGateWebhookView.as_view(), name='mygate_webhook'),

    # Export URLs
    path('orders/export/', OrderExportView.as_view(), name='order_export'),
]
