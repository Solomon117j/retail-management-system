from django.urls import path
from .views import CustomerLoginView, StaffLoginView, GenericLoginView, CustomerRegistrationView
from retail_management_system.views import CustomLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', GenericLoginView.as_view(), name='login_choice'),
    path('login/generic/', GenericLoginView.as_view(), name='login'),
    path('login/customer/', CustomerLoginView.as_view(), name='customer_login'),
    path('login/staff/', StaffLoginView.as_view(), name='staff_login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', CustomerRegistrationView.as_view(), name='customer_register'),
]
