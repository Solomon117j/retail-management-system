import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

print("=== COMPREHENSIVE LOGGING & MONITORING TEST ===")

# Test logging configuration
print("\n1. Testing Logging Configuration:")
try:
    import logging
    logger = logging.getLogger('test')
    logger.info('Test log message from monitoring test')

    # Test different loggers
    audit_logger = logging.getLogger('audit')
    audit_logger.info('Test audit log', extra={
        'user': 'test_user',
        'ip': '127.0.0.1',
        'action': 'TEST',
        'resource': '/test',
        'result': 'SUCCESS'
    })

    performance_logger = logging.getLogger('performance')
    performance_logger.info('Test performance log', extra={
        'user': 'test_user',
        'ip': '127.0.0.1',
        'method': 'GET',
        'path': '/test',
        'status_code': 200,
        'response_time': 0.1
    })

    print("✅ Logging configuration working correctly")
except Exception as e:
    print(f"❌ Logging test failed: {e}")

# Test monitoring functionality
print("\n2. Testing Monitoring System:")
try:
    from retail_management_system.monitoring import (
        system_monitor, database_monitor, application_monitor,
        health_check, performance_monitor
    )

    # Test system monitoring
    system_stats = system_monitor.get_system_stats()
    if system_stats:
        print("✅ System monitoring working")
        print(f"   CPU: {system_stats['cpu_percent']:.1f}%, Memory: {system_stats['memory_percent']:.1f}%")
    else:
        print("❌ System monitoring failed")

    # Test health check
    health_result = health_check.run_full_health_check()
    if health_result:
        print("✅ Health check working")
        print(f"   Overall status: {health_result['overall_status']}")
        for check_name, check_data in health_result['checks'].items():
            print(f"   {check_name}: {check_data['status']}")
    else:
        print("❌ Health check failed")

    # Test performance monitoring
    alerts = performance_monitor.check_performance_thresholds()
    print("✅ Performance monitoring working")
    print(f"   Active alerts: {len(alerts)}")

except Exception as e:
    print(f"❌ Monitoring test failed: {e}")

# Check log files
print("\n3. Checking Log Files:")
try:
    log_files = [
        'logs/django.log',
        'logs/security.log',
        'logs/audit.log',
        'logs/performance.log',
        'logs/error.log'
    ]

    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✅ {log_file}: {size} bytes")
        else:
            print(f"❌ {log_file}: File not found")

except Exception as e:
    print(f"❌ Log file check failed: {e}")

# Test middleware import
print("\n4. Testing Middleware Import:")
try:
    from retail_management_system.middleware.logging_middleware import (
        RequestResponseLoggingMiddleware,
        SecurityMonitoringMiddleware,
        AuditLoggingMiddleware
    )
    print("✅ Middleware classes imported successfully")
except Exception as e:
    print(f"❌ Middleware import failed: {e}")

print("\n=== TEST COMPLETE ===")
print("\nNext steps:")
print("- Check log files in the 'logs' directory")
print("- Review middleware integration in settings.py")
print("- Consider setting up log rotation and monitoring alerts")
