# Retail Management System - Complete Documentation

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Prerequisites](#3-prerequisites)
4. [Installation](#4-installation)
5. [Configuration](#5-configuration)
6. [Deployment](#6-deployment)
7. [Security](#7-security)
8. [API Documentation](#8-api-documentation)
9. [Database Schema](#9-database-schema)
10. [Monitoring & Logging](#10-monitoring--logging)
11. [Troubleshooting](#11-troubleshooting)
12. [Maintenance](#12-maintenance)

---

## 1. System Overview

The Retail Management System is a comprehensive Django-based enterprise solution for managing retail operations. Built with Python 3.13 and Django 5.2.4, this system provides end-to-end functionality for inventory management, sales processing, human resources, procurement, and business analytics across multiple store locations.

### Core Features
- **🏪 Multi-Store Management**: Centralized management with local inventory tracking
- **📦 Inventory Management**: Real-time stock tracking, product categorization, and low-stock alerts
- **👥 Human Resources**: Employee lifecycle management, attendance tracking, payroll processing
- **💰 Sales & POS**: Point-of-sale system with multiple payment gateways (MTN MoMo, PayFast, MyGate)
- **🛒 Procurement**: Supplier relationship management with dropshipping integration (DSers)
- **🛍️ E-Commerce**: Online sales platform with customer accounts and shopping cart
- **📊 Reporting & Analytics**: Comprehensive business intelligence dashboards
- **🔐 Security**: Role-based access control, comprehensive logging, and enterprise-grade security

### Technical Stack
- **Backend**: Django 5.2.4, Python 3.13
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Bootstrap 5.1.3, Font Awesome 6.0.0
- **Deployment**: Docker, Nginx, Gunicorn
- **Security**: CSRF protection, HTTPS enforcement, audit logging

---

## 2. Architecture

### System Architecture
The system follows a modular Django architecture with clean separation of concerns:

```
retail_management_system/
├── accounts/              # User authentication and authorization
├── dashboards/            # Main dashboard and landing pages
├── human_resources/       # Employee, attendance, and payroll management
├── inventory/             # Product and stock management
├── procurement/           # Supplier and purchase order management
├── sales/                 # Sales transactions and customer orders
├── store_management/      # Multi-store configuration
├── e_commerce/            # Online sales platform
├── reporting/             # Analytics and reporting
├── retail_management_system/  # Core settings and middleware
└── static/                # Static assets
```

### Database Architecture
- **PostgreSQL** for production with connection pooling
- **SQLite** for development and testing
- Comprehensive audit logging and data integrity constraints

### Security Architecture
- **Middleware Stack**: Request/response logging, security monitoring, audit logging
- **Authentication**: Django's robust auth system with custom user model
- **Authorization**: Role-based access control with granular permissions
- **File Security**: Secure file upload validation and storage

---

## 3. Prerequisites

### System Requirements
- **Operating System**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.11+ (compiled with Python 3.13 recommended)
- **Database**: PostgreSQL 15+ (production), SQLite 3+ (development)
- **Memory**: Minimum 4GB RAM, 8GB recommended
- **Storage**: 10GB free space for application and data

### Software Dependencies
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for orchestration)
- **Git**: For version control
- **SSL Certificate**: For HTTPS in production

### Network Requirements
- **Ports**: 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL)
- **Domain**: Registered domain name for production
- **SSL**: Valid SSL certificate (Let's Encrypt recommended)

---

## 4. Installation

### Quick Start (Development)

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd retail_management_system
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv env
   .\env\Scripts\activate

   # Linux/macOS
   python -m venv env
   source env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access Application**
   - Open browser: `http://127.0.0.1:8000/`
   - Login with superuser credentials

### Production Installation

For production deployment, follow the [Deployment](#6-deployment) section below.

---

## 5. Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Django Core Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/retail_db

# Payment Gateway Configuration
MTN_MOMO_API_KEY=your-mtn-momo-api-key
MTN_MOMO_API_SECRET=your-mtn-momo-api-secret
PAYFAST_MERCHANT_ID=your-payfast-merchant-id
PAYFAST_MERCHANT_KEY=your-payfast-merchant-key
MYGATE_MERCHANT_ID=your-mygate-merchant-id

# DSers Dropshipping Configuration
DSERS_API_BASE_URL=https://api.dsers.com
DSERS_API_KEY=your-dsers-api-key
DSERS_API_SECRET=your-dsers-api-secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
MAX_FILE_SIZE=5242880
ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,pdf,doc,docx
```

### Django Settings Configuration

Key settings in `retail_management_system/settings.py`:

- **Security**: HTTPS enforcement, secure cookies, CSRF protection
- **Database**: PostgreSQL with connection pooling
- **Logging**: Comprehensive logging configuration (security, audit, performance)
- **Middleware**: Custom security and monitoring middleware
- **Static Files**: Whitenoise for static file serving

### SSL Certificate Generation

For development/testing:

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout certs/devserver.key -out certs/devserver.crt -days 365 -nodes -subj "/CN=localhost"
```

For production, use Let's Encrypt or commercial certificates.

---

## 6. Deployment

### Docker Deployment (Recommended)

#### Development Environment
```bash
# Start development services
docker-compose up --build

# Access at http://localhost:8000
```

#### Production Environment
```bash
# Build and deploy production services
docker-compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput --clear
```

### Manual Production Deployment

1. **Server Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install required packages
   sudo apt install -y python3.11 python3.11-venv postgresql nginx certbot python3-certbot-nginx
   ```

2. **PostgreSQL Setup**
   ```bash
   # Create database and user
   sudo -u postgres psql
   CREATE DATABASE retail_management;
   CREATE USER retail_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE retail_management TO retail_user;
   \q
   ```

3. **Application Deployment**
   ```bash
   # Clone and setup application
   git clone <repository-url> /var/www/retail_management
   cd /var/www/retail_management

   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Setup environment variables
   cp .env.example .env
   # Edit .env with production values

   # Run migrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser --noinput
   ```

4. **Nginx Configuration**
   ```nginx
   # /etc/nginx/sites-available/retail_management
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location = /favicon.ico { access_log off; log_not_found off; }

       location /static/ {
           alias /var/www/retail_management/staticfiles/;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }

       location /media/ {
           alias /var/www/retail_management/media/;
           expires 30d;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/retail_management/retail.sock;
       }
   }
   ```

5. **Gunicorn Setup**
   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/retail_management.service

   [Unit]
   Description=Retail Management System
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/retail_management
   Environment="PATH=/var/www/retail_management/venv/bin"
   ExecStart=/var/www/retail_management/venv/bin/gunicorn --workers 3 --bind unix:/var/www/retail_management/retail.sock retail_management_system.wsgi:application

   [Install]
   WantedBy=multi-user.target

   # Enable and start service
   sudo systemctl enable retail_management
   sudo systemctl start retail_management
   ```

6. **SSL Certificate**
   ```bash
   # Obtain Let's Encrypt certificate
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

### Deployment Scripts

The project includes automated deployment scripts:

- `deploy.sh`: Production deployment script
- `deploy_staging.sh`: Staging environment deployment
- `docker-compose.yml`: Development environment
- `docker-compose.prod.yml`: Production environment

---

## 7. Security

### Security Features

#### Authentication & Authorization
- **Custom User Model**: Extended Django user model with roles
- **Role-Based Access Control**: Granular permissions system
- **Session Security**: Secure cookies with proper settings
- **Password Policies**: Strong password requirements with Argon2 hashing

#### Data Protection
- **Encryption**: Sensitive data encryption at rest
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Prevention**: Cross-site scripting protection
- **SQL Injection Prevention**: Parameterized queries

#### Network Security
- **HTTPS Enforcement**: SSL/TLS encryption in production
- **Security Headers**: Comprehensive security headers
- **Rate Limiting**: Request rate limiting (configurable)
- **IP Whitelisting**: Optional IP-based access control

#### File Security
- **Upload Validation**: File type and size validation
- **Malware Scanning**: Content-based security checks
- **Secure Storage**: Protected file storage with access controls

### Security Monitoring

#### Logging System
- **Security Logs**: Authentication and authorization events
- **Audit Logs**: Sensitive operation tracking
- **Performance Logs**: Response time and resource usage
- **Error Logs**: Application errors and exceptions

#### Automated Security Testing
- **Penetration Testing**: Automated security scans
- **Vulnerability Assessment**: Regular security audits
- **Compliance Monitoring**: Regulatory compliance checks

### Security Best Practices

1. **Regular Updates**: Keep dependencies updated
2. **Access Control**: Principle of least privilege
3. **Monitoring**: Continuous security monitoring
4. **Backup**: Regular data backups with encryption
5. **Incident Response**: Documented security incident procedures

---

## 8. API Documentation

### REST API Framework

The system includes a RESTful API framework ready for integrations:

#### Authentication
```bash
# API endpoints require authentication
Authorization: Bearer <token>
Content-Type: application/json
```

#### Available Endpoints

**Products API**
```
GET    /api/products/          # List products
POST   /api/products/          # Create product
GET    /api/products/{id}/     # Get product details
PUT    /api/products/{id}/     # Update product
DELETE /api/products/{id}/     # Delete product
```

**Orders API**
```
GET    /api/orders/            # List orders
POST   /api/orders/            # Create order
GET    /api/orders/{id}/       # Get order details
PUT    /api/orders/{id}/       # Update order status
```

**Inventory API**
```
GET    /api/inventory/         # Get inventory levels
POST   /api/inventory/adjust/  # Adjust inventory
GET    /api/inventory/alerts/  # Low stock alerts
```

#### API Response Format
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "Product Name",
        "price": 29.99,
        "stock": 100
    },
    "message": "Operation successful"
}
```

### Webhook Integration

#### DSers Dropshipping Webhooks
- **Order Status Updates**: Real-time order status notifications
- **Inventory Sync**: Automatic inventory level updates
- **Product Changes**: Product information synchronization

#### Webhook Security
- **HMAC Verification**: Request signature validation
- **IP Whitelisting**: Restrict webhook sources
- **Rate Limiting**: Prevent abuse

---

## 9. Database Schema

### Core Tables

#### User Management
- `accounts_user`: Extended user model with roles
- `accounts_employee`: Employee-specific information
- `auth_group`: User groups and permissions

#### Product Management
- `inventory_product`: Product catalog
- `inventory_category`: Product categories
- `inventory_brand`: Product brands
- `inventory_stock`: Stock levels by store

#### Sales & Orders
- `sales_sale`: Sales transactions
- `sales_saleitem`: Sale line items
- `e_commerce_onlineorder`: E-commerce orders
- `e_commerce_orderitem`: Online order items

#### Procurement
- `procurement_supplier`: Supplier information
- `procurement_purchaseorder`: Purchase orders
- `procurement_purchaseorderitem`: PO line items
- `procurement_dsersproduct`: DSers product mapping
- `procurement_dsersorder`: DSers order tracking

#### Human Resources
- `human_resources_employee`: Employee records
- `human_resources_attendance`: Attendance tracking
- `human_resources_payroll`: Payroll information

#### Store Management
- `store_management_store`: Store locations
- `store_management_storeuser`: Store-user assignments

### Database Relationships

```
User (1) ──── (M) Employee
User (1) ──── (M) StoreUser (M) ──── (1) Store

Store (1) ──── (M) Stock (M) ──── (1) Product
Product (1) ──── (M) SaleItem (M) ──── (1) Sale

Supplier (1) ──── (M) PurchaseOrder (1) ──── (M) PurchaseOrderItem
Product (1) ──── (M) PurchaseOrderItem

Product (1) ──── (1) DSersProduct (M) ──── (1) Supplier
OnlineOrder (1) ──── (M) DSersOrder
```

### Indexes and Constraints

- **Primary Keys**: Auto-incrementing integers
- **Foreign Keys**: Cascading deletes where appropriate
- **Unique Constraints**: Prevent duplicate relationships
- **Check Constraints**: Data validation at database level
- **Indexes**: Optimized for common query patterns

---

## 10. Monitoring & Logging

### Logging Configuration

The system implements comprehensive logging across multiple levels:

#### Log Types
- **Security Logs**: Authentication, authorization, suspicious activities
- **Audit Logs**: Sensitive operations and data changes
- **Performance Logs**: Response time and resource usage
- **Error Logs**: Application errors and exceptions
- **General Logs**: General application events

#### Log Format
```
SECURITY WARNING 2024-01-15 10:30:15 User:john_doe IP:192.168.1.100 Action:LOGIN_SUCCESS Resource:accounts/login Result:SUCCESS
AUDIT INFO 2024-01-15 10:30:20 User:john_doe IP:192.168.1.100 Action:CREATE Resource:inventory/product Result:SUCCESS
PERF INFO 2024-01-15 10:30:25 GET /api/products/ 200 0.234s User:john_doe IP:192.168.1.100
```

### Monitoring Tools

#### Application Monitoring
- **Django Debug Toolbar**: Development debugging
- **Custom Middleware**: Request/response monitoring
- **Performance Tracking**: Slow query identification

#### System Monitoring
- **Health Checks**: Application health endpoints
- **Resource Monitoring**: CPU, memory, disk usage
- **Database Monitoring**: Connection pooling, query performance

#### Alerting
- **Email Notifications**: Security alerts, system errors
- **Log Analysis**: Automated log parsing and alerting
- **Threshold Monitoring**: Performance and resource thresholds

### Log Rotation and Retention

- **Rotation**: Daily log rotation with compression
- **Retention**: 30 days for general logs, 90 days for security/audit logs
- **Archiving**: Compressed archives for long-term storage
- **Backup**: Encrypted log backups

---

## 11. Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test database connection
python manage.py dbshell

# Reset database connections
python manage.py shell -c "from django.db import connections; connections.close_all()"
```

#### Static Files Issues
```bash
# Collect static files
python manage.py collectstatic --noinput --clear

# Check static file permissions
ls -la staticfiles/
chmod -R 755 staticfiles/
```

#### Permission Issues
```bash
# Fix media directory permissions
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/

# Fix log directory permissions
sudo chown -R www-data:www-data logs/
sudo chmod -R 755 logs/
```

#### Performance Issues
```bash
# Check running processes
ps aux | grep gunicorn

# Monitor resource usage
top -p $(pgrep gunicorn)

# Database query optimization
python manage.py shell -c "from django.db import connection; print(connection.queries)"
```

### Debug Mode

Enable debug mode for troubleshooting:

```python
# settings.py
DEBUG = True
INTERNAL_IPS = ['127.0.0.1']
```

Access Django Debug Toolbar at `http://localhost:8000/__debug__/`

### Log Analysis

```bash
# View recent errors
tail -f logs/error.log

# Search for specific errors
grep "ERROR" logs/django.log | tail -20

# Security events
grep "SECURITY" logs/security.log | tail -10
```

---

## 12. Maintenance

### Regular Maintenance Tasks

#### Daily Tasks
- **Log Rotation**: Ensure logs are rotating properly
- **Backup Verification**: Check backup integrity
- **Security Scans**: Run automated security scans
- **Performance Monitoring**: Review system performance metrics

#### Weekly Tasks
- **Database Optimization**: Vacuum and analyze tables
- **Dependency Updates**: Check for security updates
- **Log Analysis**: Review security and audit logs
- **Storage Cleanup**: Remove temporary files

#### Monthly Tasks
- **Full Backup**: Complete system backup
- **Security Audit**: Comprehensive security assessment
- **Performance Review**: System performance analysis
- **Documentation Update**: Update system documentation

### Backup Strategy

#### Database Backup
```bash
# Automated daily backup
pg_dump retail_management > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump retail_management | gzip > backup_$(date +%Y%m%d).sql.gz
```

#### File System Backup
```bash
# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Backup static files
tar -czf static_backup_$(date +%Y%m%d).tar.gz staticfiles/
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/retail_management"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U retail_user -h localhost retail_management | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/retail_management/media/

# Configuration backup
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /var/www/retail_management/.env

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### Update Procedures

#### Minor Updates
1. **Backup current system**
2. **Update source code**: `git pull origin main`
3. **Update dependencies**: `pip install -r requirements.txt --upgrade`
4. **Run migrations**: `python manage.py migrate`
5. **Collect static files**: `python manage.py collectstatic`
6. **Restart services**: `sudo systemctl restart retail_management`

#### Major Updates
1. **Full system backup**
2. **Review release notes**
3. **Test updates in staging environment**
4. **Schedule maintenance window**
5. **Apply updates following minor update procedure**
6. **Run comprehensive tests**
7. **Monitor system for 24-48 hours**

### Performance Optimization

#### Database Optimization
```sql
-- Analyze table statistics
ANALYZE;

-- Vacuum tables
VACUUM;

-- Reindex tables
REINDEX DATABASE retail_management;
```

#### Application Optimization
- **Caching**: Implement Redis for session and template caching
- **CDN**: Use CDN for static file delivery
- **Database Indexing**: Add indexes for frequently queried fields
- **Query Optimization**: Use select_related and prefetch_related

#### System Optimization
- **Memory Tuning**: Adjust Gunicorn worker count
- **Nginx Optimization**: Configure worker processes and connections
- **SSL Optimization**: Enable HTTP/2 and OCSP stapling

---

## Support and Contact

### Technical Support
- **Documentation**: Comprehensive guides available in project repository
- **Issue Tracking**: GitHub issues for bug reports and feature requests
- **Community**: Developer community and forums

### Emergency Contacts
- **System Administrator**: admin@yourcompany.com
- **Security Team**: security@yourcompany.com
- **Development Team**: dev@yourcompany.com

### System Information
- **Version**: 1.0.0
- **Last Updated**: September 2025
- **Django Version**: 5.2.4
- **Python Version**: 3.13

---

*This documentation is maintained automatically. Please report any inaccuracies or omissions to the development team.*
