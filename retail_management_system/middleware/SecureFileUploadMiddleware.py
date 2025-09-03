import os
import magic
import logging
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('security')

class SecureFileUploadMiddleware(MiddlewareMixin):
    """
    Middleware for secure file upload handling with comprehensive security checks
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Allowed file types (MIME types)
        self.allowed_mime_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'text/plain', 'text/csv',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]

        # Dangerous file extensions to block
        self.dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
            '.php', '.asp', '.jsp', '.cgi', '.pl', '.py', '.sh', '.dll', '.so'
        ]

        # Maximum file size (10MB default)
        self.max_file_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)

        # File signature validation
        self.file_signatures = {
            'image/jpeg': [b'\xFF\xD8\xFF'],
            'image/png': [b'\x89PNG\r\n\x1a\n'],
            'image/gif': [b'GIF87a', b'GIF89a'],
            'application/pdf': [b'%PDF'],
        }

    def __call__(self, request):
        # Check for file uploads in POST requests
        if request.method == 'POST' and hasattr(request, 'FILES'):
            validation_result = self._validate_file_uploads(request)
            if not validation_result['valid']:
                logger.warning(
                    f'File upload validation failed: {validation_result["error"]}',
                    extra={
                        'user': getattr(request.user, 'username', 'Anonymous'),
                        'ip': self._get_client_ip(request),
                        'path': request.path
                    }
                )
                return HttpResponseBadRequest(f'File upload error: {validation_result["error"]}')

        response = self.get_response(request)
        return response

    def _validate_file_uploads(self, request):
        """Validate all uploaded files"""
        for field_name, uploaded_file in request.FILES.items():
            # Check file size
            if uploaded_file.size > self.max_file_size:
                return {
                    'valid': False,
                    'error': f'File {uploaded_file.name} exceeds maximum size limit of {self.max_file_size} bytes'
                }

            # Check file extension
            file_name = uploaded_file.name.lower()
            file_extension = os.path.splitext(file_name)[1]

            if file_extension in self.dangerous_extensions:
                return {
                    'valid': False,
                    'error': f'File type {file_extension} is not allowed'
                }

            # Validate MIME type using python-magic
            try:
                # Read first 1024 bytes for MIME type detection
                file_content = uploaded_file.read(1024)
                uploaded_file.seek(0)  # Reset file pointer

                detected_mime = magic.from_buffer(file_content, mime=True)

                if detected_mime not in self.allowed_mime_types:
                    return {
                        'valid': False,
                        'error': f'Invalid file type detected: {detected_mime}'
                    }

                # Additional file signature validation
                if detected_mime in self.file_signatures:
                    if not self._validate_file_signature(file_content, self.file_signatures[detected_mime]):
                        return {
                            'valid': False,
                            'error': f'File signature validation failed for {detected_mime}'
                        }

            except Exception as e:
                logger.error(f'Error during file validation: {e}')
                return {
                    'valid': False,
                    'error': 'File validation failed'
                }

            # Check for malicious content in filename
            if self._contains_malicious_filename(uploaded_file.name):
                return {
                    'valid': False,
                    'error': 'Invalid filename'
                }

        return {'valid': True}

    def _validate_file_signature(self, file_content, expected_signatures):
        """Validate file signature against expected patterns"""
        for signature in expected_signatures:
            if file_content.startswith(signature):
                return True
        return False

    def _contains_malicious_filename(self, filename):
        """Check for potentially malicious patterns in filename"""
        malicious_patterns = [
            '..', '\\', '/', '<', '>', ':', '*', '?', '"', '|',
            '\x00', '\n', '\r', '\t'
        ]

        for pattern in malicious_patterns:
            if pattern in filename:
                return True

        # Check for null bytes
        if '\x00' in filename:
            return True

        return False

    def _get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'


class FileUploadLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for logging file upload activities
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.upload_logger = logging.getLogger('uploads')

    def __call__(self, request):
        response = self.get_response(request)

        # Log successful file uploads
        if request.method == 'POST' and hasattr(request, 'FILES') and response.status_code in [200, 201]:
            for field_name, uploaded_file in request.FILES.items():
                self.upload_logger.info(
                    f'File uploaded: {uploaded_file.name}',
                    extra={
                        'user': getattr(request.user, 'username', 'Anonymous'),
                        'ip': self._get_client_ip(request),
                        'filename': uploaded_file.name,
                        'filesize': uploaded_file.size,
                        'content_type': uploaded_file.content_type,
                        'field_name': field_name
                    }
                )

        return response

    def _get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
