import time
import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('performance')
audit_logger = logging.getLogger('audit')

class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive request/response logging and performance monitoring
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_fields = [
            'password', 'token', 'key', 'secret', 'csrfmiddlewaretoken',
            'auth_token', 'api_key', 'session_key'
        ]

    def __call__(self, request):
        # Start timing
        start_time = time.time()

        # Log incoming request
        self._log_request(request)

        # Process the request
        response = self.get_response(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log response and performance
        self._log_response(request, response, response_time)

        # Log performance metrics
        self._log_performance(request, response, response_time)

        return response

    def _log_request(self, request):
        """Log incoming request details"""
        user = getattr(request.user, 'username', 'Anonymous') if hasattr(request, 'user') else 'Anonymous'
        ip = self._get_client_ip(request)

        # Log security-relevant requests
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            audit_logger.info(
                'Request received',
                extra={
                    'user': user,
                    'ip': ip,
                    'method': request.method,
                    'path': request.path,
                    'action': f'{request.method} {request.path}',
                    'resource': request.path,
                    'result': 'INITIATED'
                }
            )

        # Log sensitive data access attempts
        if any(field in request.path.lower() for field in ['admin', 'password', 'reset', 'token']):
            logger.warning(
                f'Sensitive path access: {request.method} {request.path}',
                extra={
                    'user': user,
                    'ip': ip,
                    'path': request.path,
                    'method': request.method
                }
            )

    def _log_response(self, request, response, response_time):
        """Log response details"""
        user = getattr(request.user, 'username', 'Anonymous') if hasattr(request, 'user') else 'Anonymous'
        ip = self._get_client_ip(request)

        # Log errors and security issues
        if response.status_code >= 400:
            error_logger = logging.getLogger('django.request')
            error_logger.warning(
                f'HTTP {response.status_code}: {request.method} {request.path}',
                extra={
                    'user': user,
                    'ip': ip,
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code
                }
            )

        # Log successful sensitive operations
        if response.status_code in [200, 201] and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            audit_logger.info(
                'Request completed successfully',
                extra={
                    'user': user,
                    'ip': ip,
                    'method': request.method,
                    'path': request.path,
                    'action': f'{request.method} {request.path}',
                    'resource': request.path,
                    'result': f'HTTP_{response.status_code}'
                }
            )

    def _log_performance(self, request, response, response_time):
        """Log performance metrics"""
        user = getattr(request.user, 'username', 'Anonymous') if hasattr(request, 'user') else 'Anonymous'
        ip = self._get_client_ip(request)

        # Log slow requests (>1 second)
        if response_time > 1.0:
            logger.warning(
                f'Slow request detected: {response_time:.2f}s',
                extra={
                    'user': user,
                    'ip': ip,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'response_time': response_time
                }
            )

        # Log all requests for performance monitoring
        logger.info(
            'Request processed',
            extra={
                'user': user,
                'ip': ip,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'response_time': response_time
            }
        )

    def _get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'


class SecurityMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware for enhanced security monitoring
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.security_logger = logging.getLogger('django.security')

    def __call__(self, request):
        # Check for suspicious patterns
        self._check_suspicious_activity(request)

        response = self.get_response(request)

        # Check response for security issues
        self._check_response_security(request, response)

        return response

    def _check_suspicious_activity(self, request):
        """Check for suspicious request patterns"""
        user = getattr(request.user, 'username', 'Anonymous') if hasattr(request, 'user') else 'Anonymous'
        ip = self._get_client_ip(request)

        # Check for SQL injection attempts
        sql_patterns = [
            'union', 'select', 'drop', 'insert', 'update', 'delete',
            'script', 'exec', 'xp_', 'sp_', '--', '/*', '*/'
        ]
        if any(pattern in request.path.lower() for pattern in sql_patterns):
            self.security_logger.warning(
                'Potential SQL injection attempt detected',
                extra={
                    'user': user,
                    'ip': ip,
                    'path': request.path,
                    'method': request.method
                }
            )

        # Enhanced XSS protection
        xss_patterns = [
            '<script', 'javascript:', 'onload=', 'onerror=', 'onmouseover=',
            'onmouseout=', 'onmousedown=', 'onmouseup=', 'onkeypress=',
            'onkeydown=', 'onkeyup=', 'onchange=', 'onsubmit=', 'vbscript:',
            'data:text/html', 'data:javascript', '<iframe', '<object',
            '<embed', '<form', '<input', '<meta', '<link', 'expression(',
            'javascript&colon;', 'jscript:', 'livescript:', 'mocha:',
            'vbscript&colon;', '<svg', '<math', '<xml', '<html', '<body'
        ]

        # Check POST data for XSS
        if request.method == 'POST':
            post_data = str(request.POST).lower()
            for pattern in xss_patterns:
                if pattern in post_data:
                    self.security_logger.warning(
                        f'Potential XSS attempt detected in POST data: {pattern}',
                        extra={
                            'user': user,
                            'ip': ip,
                            'path': request.path,
                            'method': request.method
                        }
                    )
                    break

        # Check GET parameters for XSS
        if request.method == 'GET':
            query_string = str(request.GET).lower()
            for pattern in xss_patterns:
                if pattern in query_string:
                    self.security_logger.warning(
                        f'Potential XSS attempt detected in GET parameters: {pattern}',
                        extra={
                            'user': user,
                            'ip': ip,
                            'path': request.path,
                            'method': request.method
                        }
                    )
                    break

        # Check headers for suspicious patterns
        suspicious_headers = ['x-forwarded-for', 'referer', 'user-agent']
        for header_name in suspicious_headers:
            header_value = request.META.get(f'HTTP_{header_name.upper().replace("-", "_")}', '')
            if header_value:
                for pattern in xss_patterns[:5]:  # Check first few patterns in headers
                    if pattern in header_value.lower():
                        self.security_logger.warning(
                            f'Suspicious header detected: {header_name}',
                            extra={
                                'user': user,
                                'ip': ip,
                                'path': request.path,
                                'method': request.method
                            }
                        )
                        break

        # Check for directory traversal
        traversal_patterns = ['../', '..\\', '%2e%2e%2f', '%2e%2e\\', '.../']
        for pattern in traversal_patterns:
            if pattern in request.path:
                self.security_logger.warning(
                    'Potential directory traversal attempt detected',
                    extra={
                        'user': user,
                        'ip': ip,
                        'path': request.path,
                        'method': request.method
                    }
                )
                break

        # Check for command injection attempts
        command_patterns = [';', '|', '`', '$(', '${', '&&', '||']
        full_path = request.path + '?' + request.META.get('QUERY_STRING', '')
        for pattern in command_patterns:
            if pattern in full_path:
                self.security_logger.warning(
                    f'Potential command injection attempt detected: {pattern}',
                    extra={
                        'user': user,
                        'ip': ip,
                        'path': request.path,
                        'method': request.method
                    }
                )
                break

    def _check_response_security(self, request, response):
        """Check response for security issues"""
        user = getattr(request.user, 'username', 'Anonymous') if hasattr(request, 'user') else 'Anonymous'
        ip = self._get_client_ip(request)

        # Check for information disclosure in error responses
        if response.status_code >= 500:
            # Log server errors but don't expose sensitive information
            self.security_logger.error(
                f'Server error {response.status_code} on {request.path}',
                extra={
                    'user': user,
                    'ip': ip,
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code
                }
            )

    def _get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive audit logging of sensitive operations
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.audit_logger = logging.getLogger('audit')

    def __call__(self, request):
        # Capture request data for audit
        self._capture_request_data(request)

        response = self.get_response(request)

        # Log audit trail for sensitive operations
        self._log_audit_trail(request, response)

        return response

    def _capture_request_data(self, request):
        """Capture important request data for audit"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            request._audit_user = request.user.username
            request._audit_user_id = request.user.id
        else:
            request._audit_user = 'Anonymous'
            request._audit_user_id = None

        request._audit_ip = self._get_client_ip(request)
        request._audit_start_time = time.time()

    def _log_audit_trail(self, request, response):
        """Log audit trail for sensitive operations"""
        sensitive_paths = [
            '/admin/', '/accounts/', '/api/auth/', '/password',
            '/user/', '/profile/', '/settings/'
        ]

        if any(path in request.path for path in sensitive_paths):
            duration = time.time() - getattr(request, '_audit_start_time', time.time())

            self.audit_logger.info(
                f'Audit: {request.method} {request.path}',
                extra={
                    'user': getattr(request, '_audit_user', 'Unknown'),
                    'ip': getattr(request, '_audit_ip', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'action': f'{request.method} {request.path}',
                    'resource': request.path,
                    'result': f'HTTP_{response.status_code}',
                    'duration': f'{duration:.2f}s'
                }
            )

    def _get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
