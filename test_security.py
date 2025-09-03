import os
import django
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

print("=== SECURITY CONFIGURATION TEST RESULTS ===")

# Test password validation
print("\n1. Password Validation Test:")
try:
    validate_password('short')
    print("❌ ERROR: Weak password 'short' was accepted")
except ValidationError as e:
    print("✅ Password validation working correctly")
    for msg in e.messages:
        print(f"   - {msg}")

# Test strong password
try:
    validate_password('MySecurePassword123!')
    print("✅ Strong password accepted")
except ValidationError as e:
    print("❌ ERROR: Strong password rejected:", e.messages)

# Test security settings
print("\n2. Security Settings Verification:")
print(f"DEBUG: {settings.DEBUG} {'✅' if not settings.DEBUG else '❌'}")
print(f"SECRET_KEY length: {len(settings.SECRET_KEY)} {'✅' if len(settings.SECRET_KEY) >= 32 else '❌'}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS} {'✅' if len(settings.ALLOWED_HOSTS) > 0 else '❌'}")

# Test production security settings
if not settings.DEBUG:
    print(f"SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', False)} {'✅' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else '❌'}")
    print(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', False)} {'✅' if getattr(settings, 'SESSION_COOKIE_SECURE', False) else '❌'}")
    print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', False)} {'✅' if getattr(settings, 'CSRF_COOKIE_SECURE', False) else '❌'}")
    print(f"SECURE_HSTS_SECONDS: {getattr(settings, 'SECURE_HSTS_SECONDS', 0)} {'✅' if getattr(settings, 'SECURE_HSTS_SECONDS', 0) >= 31536000 else '❌'}")

# Test password hashers
print(f"\n3. Password Hashers: {settings.PASSWORD_HASHERS[0]} {'✅' if 'Argon2' in settings.PASSWORD_HASHERS[0] else '❌'}")

# Test file upload security
print(f"\n4. File Upload Security:")
print(f"MAX_FILE_SIZE: {getattr(settings, 'MAX_FILE_SIZE', 0)} bytes {'✅' if getattr(settings, 'MAX_FILE_SIZE', 0) > 0 else '❌'}")
print(f"ALLOWED_FILE_TYPES: {getattr(settings, 'ALLOWED_FILE_TYPES', [])} {'✅' if len(getattr(settings, 'ALLOWED_FILE_TYPES', [])) > 0 else '❌'}")

# Test email configuration
print(f"\n5. Email Configuration:")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND} {'✅' if 'smtp' in settings.EMAIL_BACKEND else '❌'}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST} {'✅' if settings.EMAIL_HOST else '❌'}")

# Test logging configuration
print(f"\n6. Logging Configuration:")
handlers = list(settings.LOGGING['handlers'].keys())
print(f"Handlers: {handlers} {'✅' if 'security_file' in handlers else '❌'}")

print("\n=== TEST COMPLETE ===")
