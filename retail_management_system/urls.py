# project_name/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include your app's URLs under a base path
    path('stores/', include('store_management.urls')),
    path('', RedirectView.as_view(pattern_name='store_management:store_list')),
]