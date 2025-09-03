"""
Comprehensive monitoring utilities for the retail management system
"""
import psutil
import os
import logging
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class SystemMonitor:
    """System resource monitoring"""

    @staticmethod
    def get_system_stats():
        """Get comprehensive system statistics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used': psutil.virtual_memory().used,
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': psutil.disk_usage('/').percent,
                'disk_free': psutil.disk_usage('/').free,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return None

    @staticmethod
    def get_process_stats():
        """Get current process statistics"""
        try:
            process = psutil.Process()
            return {
                'pid': process.pid,
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_info': process.memory_info(),
                'num_threads': process.num_threads(),
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None,
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Error getting process stats: {e}")
            return None

class DatabaseMonitor:
    """Database connection and performance monitoring"""

    @staticmethod
    def get_db_stats():
        """Get database connection statistics"""
        try:
            with connection.cursor() as cursor:
                # Get active connections
                cursor.execute("""
                    SELECT count(*) as active_connections
                    FROM pg_stat_activity
                    WHERE state = 'active'
                """)
                active_connections = cursor.fetchone()[0]

                # Get total connections
                cursor.execute("""
                    SELECT count(*) as total_connections
                    FROM pg_stat_activity
                """)
                total_connections = cursor.fetchone()[0]

                # Get database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
                """)
                db_size = cursor.fetchone()[0]

                return {
                    'active_connections': active_connections,
                    'total_connections': total_connections,
                    'database_size': db_size,
                    'timestamp': timezone.now()
                }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return None

class ApplicationMonitor:
    """Application-specific monitoring"""

    @staticmethod
    def get_app_stats():
        """Get application statistics"""
        try:
            from django.core.cache import cache
            from django.contrib.sessions.models import Session
            from django.contrib.auth.models import User

            # Get active sessions count
            active_sessions = Session.objects.filter(
                expire_date__gt=timezone.now()
            ).count()

            # Get total users
            total_users = User.objects.count()

            # Get active users (logged in within last hour)
            active_users = User.objects.filter(
                last_login__gt=timezone.now() - timedelta(hours=1)
            ).count()

            return {
                'active_sessions': active_sessions,
                'total_users': total_users,
                'active_users': active_users,
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Error getting application stats: {e}")
            return None

class HealthCheck:
    """Comprehensive health check system"""

    @staticmethod
    def run_full_health_check():
        """Run complete health check"""
        health_status = {
            'timestamp': timezone.now(),
            'overall_status': 'healthy',
            'checks': {}
        }

        # System health
        system_stats = SystemMonitor.get_system_stats()
        if system_stats:
            health_status['checks']['system'] = {
                'status': 'healthy' if system_stats['memory_percent'] < 90 else 'warning',
                'details': system_stats
            }
        else:
            health_status['checks']['system'] = {'status': 'error', 'details': 'Unable to get system stats'}

        # Database health
        db_stats = DatabaseMonitor.get_db_stats()
        if db_stats:
            health_status['checks']['database'] = {
                'status': 'healthy',
                'details': db_stats
            }
        else:
            health_status['checks']['database'] = {'status': 'error', 'details': 'Unable to connect to database'}
            health_status['overall_status'] = 'unhealthy'

        # Application health
        app_stats = ApplicationMonitor.get_app_stats()
        if app_stats:
            health_status['checks']['application'] = {
                'status': 'healthy',
                'details': app_stats
            }
        else:
            health_status['checks']['application'] = {'status': 'error', 'details': 'Unable to get application stats'}

        # Check for any failed checks
        for check_name, check_data in health_status['checks'].items():
            if check_data['status'] == 'error':
                health_status['overall_status'] = 'unhealthy'
                break
            elif check_data['status'] == 'warning' and health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'

        return health_status

    @staticmethod
    def log_health_status(health_status):
        """Log health check results"""
        logger.info(
            f"Health check completed: {health_status['overall_status']}",
            extra={
                'health_status': health_status['overall_status'],
                'system_status': health_status['checks'].get('system', {}).get('status'),
                'database_status': health_status['checks'].get('database', {}).get('status'),
                'application_status': health_status['checks'].get('application', {}).get('status')
            }
        )

class PerformanceMonitor:
    """Performance monitoring and alerting"""

    def __init__(self):
        self.slow_request_threshold = 2.0  # seconds
        self.high_memory_threshold = 85.0  # percent
        self.high_cpu_threshold = 80.0  # percent

    def check_performance_thresholds(self):
        """Check if system is exceeding performance thresholds"""
        alerts = []

        # Get current stats
        system_stats = SystemMonitor.get_system_stats()
        if system_stats:
            if system_stats['cpu_percent'] > self.high_cpu_threshold:
                alerts.append({
                    'type': 'high_cpu',
                    'message': f"High CPU usage: {system_stats['cpu_percent']:.1f}%",
                    'value': system_stats['cpu_percent']
                })

            if system_stats['memory_percent'] > self.high_memory_threshold:
                alerts.append({
                    'type': 'high_memory',
                    'message': f"High memory usage: {system_stats['memory_percent']:.1f}%",
                    'value': system_stats['memory_percent']
                })

        return alerts

    def log_performance_alerts(self, alerts):
        """Log performance alerts"""
        for alert in alerts:
            logger.warning(
                f"Performance alert: {alert['message']}",
                extra={
                    'alert_type': alert['type'],
                    'alert_value': alert['value']
                }
            )

# Global monitor instances
system_monitor = SystemMonitor()
database_monitor = DatabaseMonitor()
application_monitor = ApplicationMonitor()
health_check = HealthCheck()
performance_monitor = PerformanceMonitor()
