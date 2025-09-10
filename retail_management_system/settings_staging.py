"""
Django settings for staging environment.
"""

import os
from .settings import *

# Override settings for staging environment
DEBUG = True

# Staging-specific allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'staging.yourdomain.com']

# Database configuration for staging
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB_STAGING', 'retail_management_staging'),
        'USER': os.environ.get('POSTGRES_USER_STAGING', 'admin_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD_STAGING', 'Only4u@12345'),
        'HOST': os.environ.get('POSTGRES_HOST_STAGING', '127.0.0.1'),
        'PORT': os.environ.get('POSTGRES_PORT_STAGING', '5432'),
    }
}

# Email configuration for staging (use test email service)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Print emails to console

# Logging level for staging
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Disable SSL redirect in staging
SECURE_SSL_REDIRECT = False

# Staging environment indicator
ENVIRONMENT = 'staging'
