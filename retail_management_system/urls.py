import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from .views import CustomLogoutView, secure_media_serve, LandingPageView
from e_commerce.views import ProductBrowseView
from .settings import BASE_DIR

# Add this safety check for LOGOUT_REDIRECT_URL
if not hasattr(settings, 'LOGOUT_REDIRECT_URL'):
    settings.LOGOUT_REDIRECT_URL = '/accounts/login/'

admin.site.site_header = "Retail Management System Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Retail Management System"

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # Landing page for public visitors
    path('', LandingPageView.as_view(), name='home'),

    # Product browse moved to /products/
    path('products/', ProductBrowseView.as_view(), name='product_browse'),
    path('hr/', include('human_resources.urls')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('analytics/', include('reporting.urls')),
    path('stores/', include('store_management.urls')),
    path('procurement/', include('procurement.urls')),
    path('sales/', include('sales.urls')),
    path('dashboards/', include('dashboards.urls', namespace='dashboards')),
    path('e_commerce/', include('e_commerce.urls', namespace='e_commerce')),
    path('__debug__/', include('debug_toolbar.urls')),

    # Favicon handler
    path('favicon.ico', lambda request: HttpResponse(status=204)),
]

# Serve static and media files in development and for production testing
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', secure_media_serve),
    ]
else:
    # Temporary static files serving for production testing only
    from django.views.static import serve
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}), 
        re_path(r'^media/(?P<path>.*)$', secure_media_serve),
    ]
