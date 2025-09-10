# Staging Environment Setup Guide

This guide explains how to set up and use the staging environment for the Retail Management System before deploying to production.

## Overview

The staging environment is configured to mirror production as closely as possible while allowing for testing and debugging. It uses:
- Separate PostgreSQL database
- Different environment variables
- Debug mode enabled
- Console email backend
- Relaxed security settings

## Files Created

### Configuration Files
- `retail_management_system/settings_staging.py` - Staging-specific Django settings
- `.env.staging` - Environment variables for staging
- `.env.production` - Environment variables for production

### Scripts
- `run_staging.py` - Script to run Django server in staging mode
- `setup_staging_db.py` - Script to set up staging database

### Modified Files
- `manage.py` - Updated to support environment switching

## Setup Instructions

### 1. Database Setup

Run the database setup script:

```bash
python setup_staging_db.py
```

This will:
- Check PostgreSQL connection
- Create staging database user
- Create staging database
- Grant necessary privileges

### 2. Run Migrations

Apply database migrations for staging:

```bash
python manage.py migrate --settings=retail_management_system.settings_staging
```

### 3. Create Superuser

Create an admin user for staging:

```bash
python manage.py createsuperuser --settings=retail_management_system.settings_staging
```

### 4. Start Staging Server

Run the staging server:

```bash
python run_staging.py
```

The server will start on `http://localhost:8000`

## Environment Configuration

### Staging Environment Variables (.env.staging)

```bash
# Django Configuration
SECRET_KEY=django-insecure-staging-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,staging.yourdomain.com

# Database Configuration
POSTGRES_DB_STAGING=retail_management_staging
POSTGRES_USER_STAGING=admin_user
POSTGRES_PASSWORD_STAGING=Only4u@12345
POSTGRES_HOST_STAGING=127.0.0.1
POSTGRES_PORT_STAGING=5432

# Email (Console backend for staging)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Other settings...
```

### Production Environment Variables (.env.production)

```bash
# Production settings with DEBUG=False, secure secrets, etc.
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# ... production database and security settings
```

## Key Differences: Staging vs Production

| Setting | Staging | Production |
|---------|---------|------------|
| DEBUG | True | False |
| ALLOWED_HOSTS | localhost, staging domain | production domain |
| Database | retail_management_staging | retail_db |
| Email Backend | Console | SMTP |
| SSL Redirect | Disabled | Enabled |
| Logging Level | DEBUG | INFO |

## Testing in Staging

### 1. Functional Testing
- Test all application features
- Verify data integrity
- Check user workflows

### 2. Performance Testing
- Load testing with realistic data
- Monitor response times
- Check resource usage

### 3. Security Testing
- Run security scans
- Test authentication flows
- Verify permissions

### 4. Integration Testing
- Test external API integrations
- Verify email functionality (check console output)
- Test file uploads

## Deployment to Production

Once staging testing is complete:

1. Update `.env.production` with production values
2. Run production database migrations
3. Collect static files: `python manage.py collectstatic --settings=retail_management_system.settings`
4. Configure web server (Nginx/Gunicorn)
5. Set up SSL certificates
6. Deploy to production server

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check database credentials in `.env.staging`
- Verify user has necessary permissions

### Migration Errors
- Check database schema compatibility
- Ensure all dependencies are installed
- Review migration files for conflicts

### Server Startup Issues
- Check Django settings syntax
- Verify all required packages are installed
- Check for port conflicts (default: 8000)

## Security Considerations

- Never commit `.env` files to version control
- Use strong, unique passwords for staging
- Regularly update dependencies
- Monitor logs for security issues

## Next Steps

After successful staging testing:
1. Document any issues found
2. Fix bugs and make improvements
3. Re-test in staging
4. Prepare production deployment
5. Monitor production after deployment

## Support

For issues with staging setup:
1. Check this documentation
2. Review error logs
3. Verify environment configuration
4. Test individual components
