# Retail Management System - Security Protocols Documentation

## Table of Contents
1. [Security Overview](#1-security-overview)
2. [Authentication & Authorization](#2-authentication--authorization)
3. [Data Protection](#3-data-protection)
4. [Network Security](#4-network-security)
5. [Application Security](#5-application-security)
6. [Database Security](#6-database-security)
7. [Audit & Monitoring](#7-audit--monitoring)
8. [Incident Response](#8-incident-response)

---

## 1. Security Overview

### 1.1 Security Framework
The Retail Management System implements a multi-layered security approach following industry best practices and Django security guidelines.

### 1.2 Security Principles
- **Defense in Depth**: Multiple security layers
- **Least Privilege**: Minimum required access
- **Fail Secure**: Secure defaults and error handling
- **Complete Mediation**: All access requests validated
- **Security by Design**: Built-in security from ground up

### 1.3 Compliance Standards
- **OWASP Top 10**: Protection against common vulnerabilities
- **Django Security**: Following Django security best practices
- **Data Protection**: GDPR-ready data handling
- **PCI DSS**: Payment card data security (if applicable)

---

## 2. Authentication & Authorization

### 2.1 User Authentication

#### Custom User Model
```python
# Custom Employee User Model
class Employee(AbstractUser):
    employee_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    # Additional security fields
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    last_password_change = models.DateTimeField(auto_now_add=True)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
```

#### Password Security
```python
# Password Validation Settings
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'custom_validators.ComplexityValidator',
        'OPTIONS': {
            'min_uppercase': 1,
            'min_lowercase': 1,
            'min_digits': 1,
            'min_special': 1,
        }
    },
]

# Password Hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

#### Account Lockout Protection
```python
class LoginAttemptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_attempts = 5
        self.lockout_duration = 30  # minutes

    def process_request(self, request):
        if request.path == '/accounts/login/' and request.method == 'POST':
            username = request.POST.get('username')
            if username:
                user = Employee.objects.filter(username=username).first()
                if user and user.is_account_locked():
                    return HttpResponse('Account locked. Try again later.', status=423)
        return None

    def process_response(self, request, response):
        if request.path == '/accounts/login/' and response.status_code == 200:
            # Reset failed attempts on successful login
            username = request.POST.get('username')
            if username:
                Employee.objects.filter(username=username).update(
                    failed_login_attempts=0,
                    account_locked_until=None
                )
        elif request.path == '/accounts/login/' and response.status_code == 401:
            # Increment failed attempts
            username = request.POST.get('username')
            if username:
                user = Employee.objects.filter(username=username).first()
                if user:
                    user.failed_login_attempts += 1
                    if user.failed_login_attempts >= self.max_attempts:
                        user.account_locked_until = timezone.now() + timedelta(minutes=self.lockout_duration)
                    user.save()
        return response
```

### 2.2 Session Management

#### Session Security Settings
```python
# Session Configuration
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = True  # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Session Engine
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Database sessions
```

#### Session Validation Middleware
```python
class SessionSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check session validity
            if not self.is_session_valid(request):
                logout(request)
                return redirect('login')
            
            # Update last activity
            request.session['last_activity'] = timezone.now().isoformat()
            
        response = self.get_response(request)
        return response

    def is_session_valid(self, request):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)
            if timezone.now() - last_activity > timedelta(hours=2):
                return False
        return True
```

### 2.3 Role-Based Access Control

#### Permission System
```python
# Custom Permissions
class EmployeePermissions:
    # HR Permissions
    CAN_MANAGE_EMPLOYEES = 'hr.manage_employees'
    CAN_VIEW_PAYROLL = 'hr.view_payroll'
    CAN_PROCESS_PAYROLL = 'hr.process_payroll'
    
    # Store Permissions
    CAN_MANAGE_STORES = 'store.manage_stores'
    CAN_MANAGE_DEPARTMENTS = 'store.manage_departments'
    
    # Inventory Permissions
    CAN_MANAGE_INVENTORY = 'inventory.manage_inventory'
    CAN_VIEW_INVENTORY = 'inventory.view_inventory'
    
    # Sales Permissions
    CAN_PROCESS_SALES = 'sales.process_sales'
    CAN_VIEW_SALES_REPORTS = 'sales.view_reports'

# Permission Decorators
def require_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage Example
@require_permission(EmployeePermissions.CAN_MANAGE_EMPLOYEES)
def employee_create_view(request):
    # View implementation
    pass
```

#### Role Hierarchy
```python
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission)
    level = models.IntegerField(default=0)  # Higher number = more privileges
    
    class Meta:
        ordering = ['-level']

# Predefined Roles
ROLES = {
    'SUPERUSER': {'level': 100, 'permissions': ['*']},
    'MANAGER': {'level': 80, 'permissions': ['hr.*', 'store.*', 'inventory.*', 'sales.view_reports']},
    'HR_MANAGER': {'level': 70, 'permissions': ['hr.*']},
    'STORE_MANAGER': {'level': 60, 'permissions': ['store.*', 'inventory.view_inventory', 'sales.view_reports']},
    'INVENTORY_MANAGER': {'level': 50, 'permissions': ['inventory.*']},
    'SALES_PERSON': {'level': 30, 'permissions': ['sales.process_sales']},
    'VIEWER': {'level': 10, 'permissions': ['*.view_*']},
}
```

---

## 3. Data Protection

### 3.1 Data Encryption

#### Database Field Encryption
```python
from cryptography.fernet import Fernet
from django.conf import settings

class EncryptedField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.cipher_suite = Fernet(settings.FIELD_ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return self.cipher_suite.decrypt(value.encode()).decode()
        except:
            return value  # Fallback for unencrypted data

    def to_python(self, value):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return str(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher_suite.encrypt(value.encode()).decode()

# Usage in Models
class Employee(AbstractUser):
    # Encrypt sensitive fields
    social_security_number = EncryptedField(max_length=255, null=True, blank=True)
    bank_account_number = EncryptedField(max_length=255, null=True, blank=True)
```

#### File Encryption
```python
import os
from cryptography.fernet import Fernet

class FileEncryption:
    def __init__(self):
        self.key = settings.FILE_ENCRYPTION_KEY
        self.cipher_suite = Fernet(self.key)

    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = self.cipher_suite.encrypt(file_data)
        
        with open(file_path + '.encrypted', 'wb') as file:
            file.write(encrypted_data)
        
        # Remove original file
        os.remove(file_path)
        return file_path + '.encrypted'

    def decrypt_file(self, encrypted_file_path):
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        
        original_path = encrypted_file_path.replace('.encrypted', '')
        with open(original_path, 'wb') as file:
            file.write(decrypted_data)
        
        return original_path
```

### 3.2 Data Validation & Sanitization

#### Input Validation
```python
from django import forms
from django.core.validators import RegexValidator
import bleach

class SecureEmployeeForm(forms.ModelForm):
    # Phone number validation
    phone = forms.CharField(
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Invalid phone number')],
        required=False
    )
    
    # Email validation (additional to built-in)
    email = forms.EmailField(
        validators=[EmailValidator(message='Invalid email format')]
    )
    
    # Salary validation
    salary = forms.DecimalField(
        min_value=0,
        max_value=999999.99,
        decimal_places=2
    )

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        # Sanitize HTML and remove potentially dangerous characters
        first_name = bleach.clean(first_name, tags=[], strip=True)
        # Remove special characters except spaces, hyphens, apostrophes
        first_name = re.sub(r'[^a-zA-Z\s\'-]', '', first_name)
        return first_name.strip()

    def clean_position(self):
        position = self.cleaned_data.get('position')
        # Sanitize and validate position
        position = bleach.clean(position, tags=[], strip=True)
        if len(position) > 50:
            raise forms.ValidationError('Position name too long')
        return position
```

#### SQL Injection Prevention
```python
# Always use Django ORM (automatically prevents SQL injection)
# GOOD:
employees = Employee.objects.filter(department__name=department_name)

# BAD (never do this):
# cursor.execute(f"SELECT * FROM employees WHERE department = '{department_name}'")

# For raw queries (when absolutely necessary), use parameterized queries:
from django.db import connection

def get_employee_stats(department_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*), AVG(salary) FROM employees WHERE department_id = %s",
            [department_id]
        )
        return cursor.fetchone()
```

### 3.3 Data Privacy & GDPR Compliance

#### Personal Data Handling
```python
class PersonalDataMixin:
    """Mixin for models containing personal data"""
    
    def anonymize(self):
        """Anonymize personal data for GDPR compliance"""
        self.first_name = f"User_{self.pk}"
        self.last_name = "Anonymized"
        self.email = f"anonymized_{self.pk}@example.com"
        self.phone = None
        self.save()

    def export_personal_data(self):
        """Export personal data for GDPR data portability"""
        return {
            'employee_id': self.employee_id,
            'name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'phone': self.phone,
            'hire_date': self.hire_date,
            'position': self.position,
            'created_at': self.date_joined,
        }

class Employee(AbstractUser, PersonalDataMixin):
    # Model implementation
    pass
```

---

## 4. Network Security

### 4.1 HTTPS Configuration

#### Production Settings
```python
# HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

#### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.2 Firewall Configuration

#### UFW (Ubuntu Firewall) Rules
```bash
# Basic firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (change port if using non-standard)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow specific database connections (if external)
sudo ufw allow from 10.0.0.0/8 to any port 5432

# Enable firewall
sudo ufw enable
```

---

## 5. Application Security

### 5.1 CSRF Protection

#### CSRF Settings
```python
# CSRF Configuration
CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']

# Custom CSRF failure view
def csrf_failure(request, reason=""):
    return render(request, 'errors/csrf_error.html', {
        'reason': reason,
        'request_path': request.path,
    }, status=403)
```

#### CSRF Token Validation
```html
<!-- All forms must include CSRF token -->
<form method="post">
    {% csrf_token %}
    <!-- Form fields -->
    <button type="submit">Submit</button>
</form>

<!-- AJAX requests -->
<script>
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Include in AJAX requests
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
</script>
```

### 5.2 XSS Protection

#### Template Auto-escaping
```html
<!-- Django templates auto-escape by default -->
<p>User input: {{ user_input }}</p>  <!-- Automatically escaped -->

<!-- Manual escaping when needed -->
<p>Safe content: {{ content|escape }}</p>

<!-- Mark as safe only when absolutely sure -->
<p>Trusted HTML: {{ trusted_html|safe }}</p>

<!-- Use format_html for dynamic HTML -->
{% load format_html %}
<p>{{ message|format_html }}</p>
```

#### Content Security Policy
```python
# CSP Middleware
class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        response['Content-Security-Policy'] = csp_policy
        return response
```

### 5.3 File Upload Security

#### Secure File Handling
```python
import os
import magic
from django.core.exceptions import ValidationError

class SecureFileUpload:
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def validate_file(uploaded_file):
        # Check file size
        if uploaded_file.size > SecureFileUpload.MAX_FILE_SIZE:
            raise ValidationError('File too large. Maximum size is 5MB.')
        
        # Check file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in SecureFileUpload.ALLOWED_EXTENSIONS:
            raise ValidationError('File type not allowed.')
        
        # Check MIME type
        file_mime = magic.from_buffer(uploaded_file.read(1024), mime=True)
        uploaded_file.seek(0)  # Reset file pointer
        
        allowed_mimes = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
        }
        
        expected_mime = allowed_mimes.get(file_extension)
        if expected_mime and file_mime != expected_mime:
            raise ValidationError('File content does not match extension.')
        
        return True

    @staticmethod
    def secure_filename(filename):
        """Generate secure filename"""
        import uuid
        import time
        
        # Get file extension
        _, ext = os.path.splitext(filename)
        
        # Generate unique filename
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{timestamp}_{unique_id}{ext}"

# Usage in forms
class EmployeePhotoForm(forms.ModelForm):
    photo = forms.ImageField(required=False)
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            SecureFileUpload.validate_file(photo)
        return photo
```

---

## 6. Database Security

### 6.1 Database Configuration

#### Secure Database Settings
```python
# Database Security Settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,
    }
}

# Connection pooling for production
if not DEBUG:
    DATABASES['default']['OPTIONS'].update({
        'MAX_CONNS': 20,
        'MIN_CONNS': 5,
    })
```

#### Database User Permissions
```sql
-- Create dedicated database user with minimal privileges
CREATE USER retail_app WITH PASSWORD 'strong_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE retail_db TO retail_app;
GRANT USAGE ON SCHEMA public TO retail_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO retail_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO retail_app;

-- Revoke dangerous permissions
REVOKE CREATE ON SCHEMA public FROM retail_app;
REVOKE ALL ON SCHEMA information_schema FROM retail_app;
REVOKE ALL ON SCHEMA pg_catalog FROM retail_app;
```

### 6.2 Query Security

#### Parameterized Queries
```python
# Always use Django ORM or parameterized queries
from django.db import connection

def secure_query_example(user_id, status):
    # SECURE: Using Django ORM
    employees = Employee.objects.filter(
        id=user_id,
        is_active=status
    )
    
    # SECURE: Using parameterized raw query when necessary
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM employees WHERE id = %s AND is_active = %s",
            [user_id, status]
        )
        results = cursor.fetchall()
    
    return results

# NEVER do this (SQL injection vulnerability):
# cursor.execute(f"SELECT * FROM employees WHERE id = {user_id}")
```

### 6.3 Database Backup Security

#### Encrypted Backups
```bash
#!/bin/bash
# Secure backup script

DB_NAME="retail_db"
BACKUP_DIR="/secure/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"
ENCRYPTED_FILE="$BACKUP_FILE.gpg"

# Create backup
pg_dump $DB_NAME > $BACKUP_FILE

# Encrypt backup
gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 \
    --s2k-digest-algo SHA512 --s2k-count 65536 --symmetric \
    --output $ENCRYPTED_FILE $BACKUP_FILE

# Remove unencrypted backup
rm $BACKUP_FILE

# Set secure permissions
chmod 600 $ENCRYPTED_FILE

# Remove old backups (keep last 30 days)
find $BACKUP_DIR -name "backup_*.sql.gpg" -mtime +30 -delete
```

---

## 7. Audit & Monitoring

### 7.1 Security Logging

#### Audit Log Model
```python
class SecurityAuditLog(models.Model):
    ACTIONS = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('LOGIN_FAILED', 'Failed Login Attempt'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('PERMISSION_DENIED', 'Permission Denied'),
        ('DATA_ACCESS', 'Data Access'),
        ('DATA_MODIFY', 'Data Modification'),
        ('DATA_DELETE', 'Data Deletion'),
        ('ADMIN_ACTION', 'Admin Action'),
        ('SECURITY_VIOLATION', 'Security Violation'),
    ]
    
    user = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTIONS)
    resource = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

# Audit logging utility
class SecurityLogger:
    @staticmethod
    def log_event(request, action, resource='', details=None, success=True):
        SecurityAuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            resource=resource,
            ip_address=SecurityLogger.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details=details or {},
            success=success
        )
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

#### Audit Middleware
```python
class SecurityAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Log response
        duration = time.time() - start_time
        
        # Log security-relevant events
        if response.status_code == 403:
            SecurityLogger.log_event(
                request, 
                'PERMISSION_DENIED', 
                request.path,
                {'status_code': response.status_code, 'duration': duration},
                success=False
            )
        elif response.status_code >= 400:
            SecurityLogger.log_event(
                request,
                'SECURITY_VIOLATION',
                request.path,
                {'status_code': response.status_code, 'duration': duration},
                success=False
            )
        
        return response
```

### 7.2 Intrusion Detection

#### Suspicious Activity Detection
```python
class IntrusionDetection:
    @staticmethod
    def detect_brute_force(ip_address, time_window=300):
        """Detect brute force attacks"""
        recent_failures = SecurityAuditLog.objects.filter(
            ip_address=ip_address,
            action='LOGIN_FAILED',
            timestamp__gte=timezone.now() - timedelta(seconds=time_window)
        ).count()
        
        if recent_failures >= 10:
            IntrusionDetection.block_ip(ip_address)
            return True
        return False
    
    @staticmethod
    def detect_sql_injection(request):
        """Detect SQL injection attempts"""
        sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bor\b.*=.*)",
            r"(';.*--)",
        ]
        
        query_string = request.META.get('QUERY_STRING', '').lower()
        post_data = str(request.POST).lower()
        
        for pattern in sql_patterns:
            if re.search(pattern, query_string) or re.search(pattern, post_data):
                SecurityLogger.log_event(
                    request,
                    'SECURITY_VIOLATION',
                    'SQL_INJECTION_ATTEMPT',
                    {'pattern': pattern, 'query': query_string},
                    success=False
                )
                return True
        return False
    
    @staticmethod
    def block_ip(ip_address, duration=3600):
        """Block IP address"""
        BlockedIP.objects.create(
            ip_address=ip_address,
            blocked_until=timezone.now() + timedelta(seconds=duration),
            reason='Suspicious activity detected'
        )
```

### 7.3 Security Monitoring Dashboard

#### Security Metrics
```python
class SecurityMetrics:
    @staticmethod
    def get_security_summary(days=7):
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return {
            'total_logins': SecurityAuditLog.objects.filter(
                action='LOGIN',
                timestamp__range=[start_date, end_date]
            ).count(),
            
            'failed_logins': SecurityAuditLog.objects.filter(
                action='LOGIN_FAILED',
                timestamp__range=[start_date, end_date]
            ).count(),
            
            'permission_denials': SecurityAuditLog.objects.filter(
                action='PERMISSION_DENIED',
                timestamp__range=[start_date, end_date]
            ).count(),
            
            'security_violations': SecurityAuditLog.objects.filter(
                action='SECURITY_VIOLATION',
                timestamp__range=[start_date, end_date]
            ).count(),
            
            'unique_users': SecurityAuditLog.objects.filter(
                timestamp__range=[start_date, end_date]
            ).values('user').distinct().count(),
            
            'top_ips': SecurityAuditLog.objects.filter(
                timestamp__range=[start_date, end_date]
            ).values('ip_address').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
        }
```

---

## 8. Incident Response

### 8.1 Incident Response Plan

#### Security Incident Classification
```python
class SecurityIncident(models.Model):
    SEVERITY_LEVELS = [
        ('LOW', 'Low - Minor security issue'),
        ('MEDIUM', 'Medium - Moderate security concern'),
        ('HIGH', 'High - Significant security threat'),
        ('CRITICAL', 'Critical - Immediate action required'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('INVESTIGATING', 'Under Investigation'),
        ('CONTAINED', 'Contained'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    incident_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPEN')
    affected_systems = models.JSONField(default=list)
    discovered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    
    def generate_incident_id(self):
        """Generate unique incident ID"""
        date_str = timezone.now().strftime('%Y%m%d')
        count = SecurityIncident.objects.filter(
            discovered_at__date=timezone.now().date()
        ).count() + 1
        return f"SEC-{date_str}-{count:03d}"
```

#### Automated Response Actions
```python
class AutomatedResponse:
    @staticmethod
    def handle_brute_force_attack(ip_address):
        """Automated response to brute force attacks"""
        # Block IP address
        IntrusionDetection.block_ip(ip_address, duration=7200)  # 2 hours
        
        # Create security incident
        incident = SecurityIncident.objects.create(
            incident_id=SecurityIncident().generate_incident_id(),
            title=f"Brute Force Attack from {ip_address}",
            description=f"Multiple failed login attempts detected from IP {ip_address}",
            severity='HIGH',
            affected_systems=['authentication'],
        )
        
        # Send alert
        SecurityAlerts.send_alert(
            'BRUTE_FORCE_ATTACK',
            f"IP {ip_address} has been blocked due to brute force attack",
            incident
        )
    
    @staticmethod
    def handle_sql_injection_attempt(request):
        """Automated response to SQL injection attempts"""
        ip_address = SecurityLogger.get_client_ip(request)
        
        # Block IP immediately for SQL injection attempts
        IntrusionDetection.block_ip(ip_address, duration=86400)  # 24 hours
        
        # Create critical incident
        incident = SecurityIncident.objects.create(
            incident_id=SecurityIncident().generate_incident_id(),
            title=f"SQL Injection Attempt from {ip_address}",
            description=f"SQL injection attempt detected from IP {ip_address}",
            severity='CRITICAL',
            affected_systems=['database', 'application'],
        )
        
        # Send immediate alert
        SecurityAlerts.send_critical_alert(
            'SQL_INJECTION_ATTEMPT',
            f"CRITICAL: SQL injection attempt from {ip_address}",
            incident
        )
```

### 8.2 Security Alerts

#### Alert System
```python
class SecurityAlerts:
    @staticmethod
    def send_alert(alert_type, message, incident=None):
        """Send security alert to administrators"""
        recipients = Employee.objects.filter(
            is_superuser=True,
            is_active=True
        ).values_list('email', flat=True)
        
        subject = f"Security Alert: {alert_type}"
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.SECURITY_EMAIL_FROM,
            recipient_list=recipients,
            fail_silently=False,
        )
        
        # Log alert
        SecurityAuditLog.objects.create(
            action='SECURITY_ALERT',
            resource=alert_type,
            details={
                'message': message,
                'incident_id': incident.incident_id if incident else None,
                'recipients': list(recipients),
            }
        )
    
    @staticmethod
    def send_critical_alert(alert_type, message, incident=None):
        """Send critical security alert with SMS notification"""
        # Send email alert
        SecurityAlerts.send_alert(alert_type, message, incident)
        
        # Send SMS to security team (implement SMS service)
        security_phones = Employee.objects.filter(
            groups__name='Security Team',
            is_active=True
        ).values_list('phone', flat=True)
        
        for phone in security_phones:
            # SMSService.send_sms(phone, f"CRITICAL SECURITY ALERT: {message}")
            pass
```

### 8.3 Recovery Procedures

#### System Recovery Checklist
```python
class RecoveryProcedures:
    @staticmethod
    def initiate_lockdown():
        """Emergency system lockdown"""
        # Disable all non-admin users
        Employee.objects.filter(is_superuser=False).update(is_active=False)
        
        # Clear all active sessions
        Session.objects.all().delete()
        
        # Enable maintenance mode
        cache.set('maintenance_mode', True, timeout=None)
        
        # Log lockdown
        SecurityAuditLog.objects.create(
            action='SYSTEM_LOCKDOWN',
            resource='ENTIRE_SYSTEM',
            details={'reason': 'Emergency security lockdown'},
        )
    
    @staticmethod
    def restore_from_backup(backup_date):
        """Restore system from backup"""
        # Implementation depends on backup strategy
        # This is a placeholder for the recovery process
        pass
    
    @staticmethod
    def security_audit_post_incident():
        """Perform security audit after incident"""
        audit_results = {
            'user_accounts_reviewed': True,
            'permissions_verified': True,
            'logs_analyzed': True,
            'vulnerabilities_patched': True,
            'security_policies_updated': True,
        }
        
        return audit_results
```

---

## Security Checklist

### Daily Security Tasks
- [ ] Review security logs for anomalies
- [ ] Check failed login attempts
- [ ] Verify backup completion
- [ ] Monitor system performance
- [ ] Review active user sessions

### Weekly Security Tasks
- [ ] Update security patches
- [ ] Review user permissions
- [ ] Analyze security metrics
- [ ] Test backup restoration
- [ ] Review security incidents

### Monthly Security Tasks
- [ ] Security audit
- [ ] Penetration testing
- [ ] Update security policies
- [ ] Security training for staff
- [ ] Review and update incident response plan

### Quarterly Security Tasks
- [ ] Comprehensive security assessment
- [ ] Update security documentation
- [ ] Review and update access controls
- [ ] Security awareness training
- [ ] Disaster recovery testing

---

*Document Version: 1.0*  
*Last Updated: December 2024*  
*Prepared by: Security Team*