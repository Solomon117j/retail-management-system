from django.urls import path
from .views import DashboardView
from django.contrib.auth.decorators import login_required

app_name = 'dashboards'

urlpatterns = [
	path('', login_required(DashboardView.as_view()), name='dashboard'),
    
]

