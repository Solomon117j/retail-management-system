from django.urls import path
from .views import DashboardView, SecurityDashboardView, SecurityMetricsAPIView
from django.contrib.auth.decorators import login_required

app_name = 'dashboards'

urlpatterns = [
	path('', login_required(DashboardView.as_view()), name='dashboard'),
	path('security/', login_required(SecurityDashboardView.as_view()), name='security_dashboard'),
	path('api/security-metrics/', SecurityMetricsAPIView.as_view(), name='security_metrics_api'),
]

