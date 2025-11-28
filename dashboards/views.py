# core/views.py
import os
import json
from datetime import datetime, timedelta
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.conf import settings
from store_management.models import Store
from human_resources.models import Employee
from inventory.models import Product
from procurement.models import Supplier
from sales.models import Sale, Customer
from e_commerce.models import OnlineOrder
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def htmx_counter(request):
    """Simple HTMX demo: store a counter in session and return a fragment."""
    count = request.session.get('htmx_counter', 0)
    # If an increment is requested, increment and save
    if request.GET.get('increment'):
        try:
            count = int(count) + 1
        except Exception:
            count = 1
        request.session['htmx_counter'] = count

    # Render fragment
    return render(request, 'htmx/counter_fragment.html', {'count': count})

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get stats from different apps
        context['store_count'] = Store.objects.count()
        context['employee_count'] = Employee.objects.filter(is_active=True).count()
        context['inventory_count'] = Product.objects.count()
        context['supplier_count'] = Supplier.objects.filter(is_active=True).count()
        context['sales_count'] = Sale.objects.count()
        context['customer_count'] = Customer.objects.count()
        context['online_orders_count'] = OnlineOrder.objects.count()

        # Add recent pending online orders for staff dashboard
        if not self.request.user.is_customer:
            context['recent_online_orders'] = OnlineOrder.objects.filter(
                status__in=['pending', 'processing']
            ).select_related('customer').order_by('-order_date')[:10]
        else:
            context['recent_online_orders'] = []

        return context

class SecurityDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/security.html'

    def test_func(self):
        """Only allow staff users to access security dashboard"""
        return not self.request.user.is_customer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Security metrics
        context['security_metrics'] = self._get_security_metrics()
        context['recent_security_events'] = self._get_recent_security_events()
        context['failed_login_attempts'] = self._get_failed_login_attempts()
        context['suspicious_activities'] = self._get_suspicious_activities()

        return context

    def _get_security_metrics(self):
        """Get security-related metrics"""
        # This would typically read from log files or a security events database
        # For now, return mock data based on log analysis
        return {
            'total_security_events_today': 0,
            'failed_login_attempts_today': 0,
            'suspicious_requests_today': 0,
            'blocked_ips_today': 0,
            'active_sessions': 0,
            'security_score': 85  # Mock security score
        }

    def _get_recent_security_events(self):
        """Get recent security events from logs"""
        events = []
        # In a real implementation, this would parse log files
        # For now, return sample events
        events.append({
            'timestamp': datetime.now() - timedelta(minutes=5),
            'event_type': 'Login Attempt',
            'severity': 'INFO',
            'message': 'Successful login for user: admin',
            'ip': '192.168.1.100'
        })
        return events

    def _get_failed_login_attempts(self):
        """Get failed login attempts"""
        return []  # Would parse logs for failed login patterns

    def _get_suspicious_activities(self):
        """Get suspicious activities"""
        return []  # Would parse logs for suspicious patterns

class SecurityMetricsAPIView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """API endpoint for security metrics data"""

    def test_func(self):
        return not self.request.user.is_customer

    def get(self, request, *args, **kwargs):
        """Return security metrics as JSON"""
        metrics = {
            'security_events': self._get_security_events_data(),
            'performance_metrics': self._get_performance_data(),
            'system_health': self._get_system_health_data()
        }
        return JsonResponse(metrics)

    def _get_security_events_data(self):
        """Get security events data for charts"""
        return {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'datasets': [{
                'label': 'Security Events',
                'data': [12, 19, 3, 5, 2, 3, 9],
                'borderColor': 'rgb(255, 99, 132)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            }]
        }

    def _get_performance_data(self):
        """Get performance metrics data"""
        return {
            'labels': ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            'datasets': [{
                'label': 'Response Time (ms)',
                'data': [120, 150, 180, 200, 160, 140],
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            }]
        }

    def _get_system_health_data(self):
        """Get system health data"""
        return {
            'cpu_usage': 45,
            'memory_usage': 60,
            'disk_usage': 30,
            'network_connections': 25
        }
