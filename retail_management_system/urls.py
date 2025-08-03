# retail_management_system/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings  # Import settings module
from .views import DashboardView, CustomLogoutView

# Add this safety check for LOGOUT_REDIRECT_URL
if not hasattr(settings, 'LOGOUT_REDIRECT_URL'):
    settings.LOGOUT_REDIRECT_URL = '/accounts/login/'

admin.site.site_header = "Retail Management System Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Retail Management System"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include([
        path('login/', auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ), name='login'),
        path('logout/', CustomLogoutView.as_view(), name='logout'),
    ])),
    path('', DashboardView.as_view(), name='dashboard'),
    path('', RedirectView.as_view(url='/stores/')),
    path('hr/', include('human_resources.urls')),
    path('inventory/', include('inventory.urls')),
    path('analytics/', include('reporting.urls')),
    
    path('stores/', include('store_management.urls')),
    path('procurement/', include('procurement.urls')),
    path('sales/', include('sales.urls')),
    path('e_commerce/', include('e_commerce.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    
]



