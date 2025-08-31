# Retail Management System - Comprehensive Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Module Documentation](#module-documentation)
4. [Database Schema](#database-schema)
5. [User Management & Authentication](#user-management--authentication)
6. [Business Workflows](#business-workflows)
7. [API Endpoints](#api-endpoints)
8. [Security & Permissions](#security--permissions)
9. [Installation & Setup](#installation--setup)
10. [Configuration](#configuration)
11. [Deployment](#deployment)
12. [Maintenance & Troubleshooting](#maintenance--troubleshooting)

---

## System Overview

The Retail Management System is a comprehensive Django-based enterprise solution designed to manage all aspects of retail operations. The system provides end-to-end functionality for inventory management, sales processing, human resources, procurement, and business analytics.

### Key Features
- **Multi-store support** with centralized management
- **Real-time inventory tracking** across all locations
- **Integrated POS system** with offline capability
- **Employee management** with attendance and payroll
- **Supplier relationship management**
- **Comprehensive reporting and analytics**
- **E-commerce integration**
- **Role-based access control**

### Target Users
- **Store Managers**: Daily operations, inventory, sales
- **HR Personnel**: Employee management, payroll, attendance
- **Procurement Officers**: Supplier management, purchase orders
- **Administrators**: System configuration, user management
- **Executives**: Reports, analytics, business insights

---

## Architecture & Technology Stack

### Backend Framework
- **Django 4.x**: Primary web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management

### Frontend Technologies
- **Django Templates**: Server-side rendering
- **Bootstrap 5**: Responsive UI framework
- **jQuery**: JavaScript utilities
- **Chart.js**: Data visualization

### Development Tools
- **Python 3.9+**: Programming language
- **pip**: Package management
- **Git**: Version control
- **Docker**: Containerization support

### System Architecture
```
┌─────────────────────────────────────────┐
│           Load Balancer                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Web Server (Nginx)             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Django Application              │
│  ┌─────────────┬─────────────┐        │
│  │   WSGI      │   Django    │        │
│  │  Server     │   App       │        │
│  └─────────────┴─────────────┘        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Database Layer                  │
│  ┌─────────────┬─────────────┐        │
│  │ PostgreSQL  │    Redis    │        │
│  │  Primary    │   Cache     │        │
│  └─────────────┴─────────────┘        │
└─────────────────────────────────────────┘
```

---

## Module Documentation

### 1. Accounts Module (`accounts/`)
**Purpose**: User authentication and authorization management

**Key Models**:
- `User`: Extended Django user model with additional fields
- `UserProfile`: Additional user information and preferences

**Features**:
- User registration and authentication
- Password reset functionality
- Profile management
- Role-based permissions

### 2. Inventory Module (`inventory/`)
**Purpose**: Stock and inventory management across all stores

**Key Models**:
- `Product`: Product catalog with variants
- `Stock`: Inventory levels per store
- `StockMovement`: Track all inventory changes
- `Category`: Product categorization

**Features**:
- Real-time stock tracking
- Low stock alerts
- Barcode scanning support
- Multi-location inventory
- Stock adjustments and transfers

### 3. Sales Module (`sales/`)
**Purpose**: Point of sale and transaction processing

**Key Models**:
- `Sale`: Complete transaction records
- `SaleItem`: Individual line items
- `SalesTransaction`: Payment processing

**Features**:
- POS interface for cashiers
- Multiple payment methods
- Receipt generation
- Returns and refunds
- Sales analytics

### 4. Human Resources Module (`human_resources/`)
**Purpose**: Employee lifecycle management

**Key Models**:
- `Employee`: Staff information and records
- `Attendance`: Daily attendance tracking
- `Payroll`: Salary processing and payslips
- `Leave`: Leave management system

**Features**:
- Employee onboarding
- Attendance tracking (biometric/RFID)
- Payroll calculation
- Leave management
- Performance tracking

### 5. Procurement Module (`procurement/`)
**Purpose**: Supplier and purchase order management

**Key Models**:
- `Supplier`: Vendor information
- `PurchaseOrder`: Purchase order management
- `PurchaseItem`: Order line items

**Features**:
- Supplier relationship management
- Purchase order creation
- Delivery tracking
- Supplier performance metrics

### 6. Store Management (`store_management/`)
**Purpose**: Individual store operations and settings

**Key Models**:
- `Store`: Store information and configuration
- `StoreSettings`: Store-specific settings

**Features**:
- Multi-store support
- Store-specific pricing
- Local inventory management
- Store performance tracking

### 7. E-commerce (`e_commerce/`)
**Purpose**: Online sales platform integration

**Key Models**:
- `CustomerAccount`: Online customer profiles
- `OnlineOrder`: Web-based orders

**Features**:
- Online catalog
- Shopping cart functionality
- Payment gateway integration
- Order fulfillment

### 8. Reporting (`reporting/`)
**Purpose**: Business intelligence and analytics

**Features**:
- Sales reports
- Inventory reports
- Employee reports
- Financial analytics
- Custom report builder

### 9. Dashboards (`dashboards/`)
**Purpose**: Executive and operational dashboards

**Features**:
- Real-time KPI monitoring
- Sales performance dashboards
- Inventory alerts
- Employee attendance overview

---

## Database Schema

### Core Entity Relationships

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Store    │────<│   Product   │>────│  Category   │
└─────────────┘     └─────────────┘     └─────────────┘
        │                    │
        │                    >────┌─────────────┐
        │                         │    Stock    │
        │                         └─────────────┘
        │                                │
┌─────────────┐     ┌─────────────┐     │
│  Employee   │────<│   Payroll   │<────┘
└─────────────┘     └─────────────┘
        │
        >────┌─────────────┐
             │ Attendance  │
             └─────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Supplier  │────<│PurchaseOrder│>────│    Sale     │
└─────────────┘     └─────────────┘     └─────────────┘
                            │                    │
                            │                    >────┌─────────────┐
                            │                         │SaleTransaction│
                            │                         └─────────────┘
```

### Key Tables Overview

| Table Name | Purpose | Key Fields |
|------------|---------|------------|
| `auth_user` | User authentication | username, email, password |
| `inventory_product` | Product catalog | name, sku, price, category |
| `inventory_stock` | Inventory levels | product_id, store_id, quantity |
| `sales_sale` | Transaction records | total_amount, payment_method, timestamp |
| `hr_employee` | Employee information | name, email, store_id, position |
| `hr_payroll` | Salary processing | employee_id, basic_salary, allowances |

---

## User Management & Authentication

### User Roles & Permissions

| Role | Permissions | Description |
|------|-------------|-------------|
| **Super Admin** | Full system access | Complete control over all modules |
| **Store Manager** | Store operations | Inventory, sales, employees |
| **Cashier** | POS operations | Process sales, view products |
| **HR Manager** | HR functions | Employee management, payroll |
| **Procurement Officer** | Purchasing | Suppliers, purchase orders |
| **Accountant** | Financial | Reports, payroll approval |
| **Viewer** | Read-only | Dashboards and reports |

### Authentication Flow
1. User submits credentials via login form
2. System validates against Django authentication
3. Role-based permissions are loaded
4. Redirect to appropriate dashboard
5. Session management with Redis

---

## Business Workflows

### 1. Product Lifecycle Workflow
```
New Product → Add to Catalog → Set Initial Stock → Set Pricing → Available for Sale
     ↓              ↓              ↓              ↓              ↓
  Supplier    Quality Check    Stock Entry    Price Update    POS/E-commerce
```

### 2. Sales Process Workflow
```
Customer Purchase → Scan Items → Calculate Total → Process Payment → Generate Receipt
        ↓              ↓              ↓              ↓              ↓
   Inventory Check   Update Stock   Apply Discount   Record Sale   Update Analytics
```

### 3. Employee Management Workflow
```
New Hire → Create Employee Record → Set Schedule → Track Attendance → Process Payroll
    ↓              ↓              ↓              ↓              ↓
  Onboarding    HR Approval    Shift Planning    Daily Check-in    Monthly Processing
```

### 4. Procurement Workflow
```
Low Stock Alert → Create PO → Send to Supplier → Receive Goods → Update Inventory
        ↓              ↓              ↓              ↓              ↓
   System Detection   Manager Approval   Email Notification   Quality Check   Stock Update
```

---

## API Endpoints

### Authentication Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login/` | POST | User authentication |
| `/api/auth/logout/` | POST | User logout |
| `/api/auth/password/reset/` | POST | Password reset request |

### Inventory Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/inventory/products/` | GET, POST | Product listing and creation |
| `/api/inventory/stock/` | GET, PUT | Stock levels and updates |
| `/api/inventory/categories/` | GET | Product categories |

### Sales Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sales/transactions/` | GET, POST | Sales records |
| `/api/sales/receipts/<id>/` | GET | Receipt details |
| `/api/sales/refunds/` | POST | Process refunds |

### HR Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/hr/employees/` | GET, POST | Employee management |
| `/api/hr/attendance/` | GET, POST | Attendance records |
| `/api/hr/payroll/` | GET, POST | Payroll processing |

---

## Security & Permissions

### Security Features
- **CSRF Protection**: All forms include CSRF tokens
- **SQL Injection Prevention**: Django ORM with parameterized queries
- **XSS Protection**: Template auto-escaping
- **Rate Limiting**: API endpoint throttling
- **HTTPS Enforcement**: SSL/TLS encryption
- **Secure Password Storage**: PBKDF2 password hashing

### Permission Matrix

| Module | Super Admin | Store Manager | Cashier | HR Manager |
|--------|-------------|---------------|---------|------------|
| **Products** | CRUD | CRUD | R | R |
| **Inventory** | CRUD | CRUD | R | - |
| **Sales** | CRUD | CRUD | CR | R |
| **Employees** | CRUD | CRUD | - | CRUD |
| **Payroll** | CRUD | R | - | CRUD |
| **Reports** | CRUD | CRUD | R | CRUD |

---

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- Redis server
- Node.js (for frontend assets)

### Installation Steps

1. **Clone the Repository**
```bash
git clone <repository-url>
cd retail_management_system
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Database Setup**
```bash
# Create PostgreSQL database
createdb retail_management

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

5. **Create Superuser**
```bash
python manage.py createsuperuser
```

6. **Load Initial Data**
```bash
python manage.py loaddata fixtures/initial_data.json
```

7. **Collect Static Files**
```bash
python manage.py collectstatic
```

8. **Run Development Server**
```bash
python manage.py runserver
```

---

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/retail_management
REDIS_URL=redis://localhost:6379/0

# Security Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway
STRIPE_PUBLIC_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
```

### Settings Configuration
Key settings in `settings.py`:

```python
# Core settings
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom apps
    'accounts',
    'inventory',
    'sales',
    'human_resources',
    'procurement',
    'e_commerce',
    'dashboards',
    'reporting',
]

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## Deployment

### Production Deployment Checklist

1. **Security Hardening**
   - [ ] Set `DEBUG=False`
   - [ ] Configure proper `ALLOWED_HOSTS`
   - [ ] Set up SSL certificates
   - [ ] Configure firewall rules

2. **Performance Optimization**
   - [ ] Enable Gzip compression
   - [ ] Configure CDN for static files
   - [ ] Set up database connection pooling
   - [ ] Enable caching with Redis

3. **Monitoring Setup**
   - [ ] Configure error logging (Sentry)
   - [ ] Set up performance monitoring
   - [ ] Configure backup automation
   - [ ] Set up health checks

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "retail_management_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/retail_management
      - REDIS_URL=redis://redis:6379/0

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=retail_management
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

volumes:
  postgres_data:
```

---

## Maintenance & Troubleshooting

### Regular Maintenance Tasks

#### Daily
- Check system health status
- Review error logs
- Monitor disk space
- Verify backup completion

#### Weekly
- Update security patches
- Review performance metrics
- Clean up old sessions
- Check database integrity

#### Monthly
- Full system backup
- Security audit
- Performance optimization review
- Update documentation

### Common Issues & Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Database Connection Error** | "could not connect to database" | Check PostgreSQL service, verify credentials |
| **Static Files Not Loading** | Missing CSS/JS | Run `collectstatic`, check nginx configuration |
| **Permission Denied** | 403 Forbidden | Check user permissions, verify group membership |
| **Memory Issues** | Slow performance | Increase server memory, optimize queries |
| **Email Not Sending** | Failed notifications | Check email configuration, verify SMTP settings |

### Log Files Location
- **Application Logs**: `/var/log/retail_management/app.log`
- **Error Logs**: `/var/log/retail_management/error.log`
- **Access Logs**: `/var/log/nginx/access.log`
- **Database Logs**: `/var/log/postgresql/postgresql.log`

### Backup Strategy

#### Database Backup
```bash
# Daily backup
pg_dump retail_management > backup_$(date +%Y%m%d).sql

# Restore from backup
psql retail_management < backup_20240101.sql
```

#### File Backup
```bash
# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Backup static files
tar -czf static_backup_$(date +%Y%m%d).tar.gz staticfiles/
```

---

## Support & Contact

### Technical Support
- **Documentation**: [System Wiki](https://wiki.yourcompany.com)
- **Issue Tracker**: [GitHub Issues](https://github.com/yourcompany/retail_management/issues)
- **Email**: support@yourcompany.com

### Training Resources
- **User Manual**: Available in the `/docs` directory
- **Video Tutorials**: [Training Portal](https://training.yourcompany.com)
- **API Documentation**: Available at `/api/docs/` when running

### Community
- **Developer Forum**: [Community Forum](https://forum.yourcompany.com)
- **Feature Requests**: [Product Roadmap](https://roadmap.yourcompany.com)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | 2024-01-15 | Initial release |
| **1.1.0** | 2024-02-01 | Added e-commerce module |
| **1.2.0** | 2024-03-15 | Enhanced reporting features |
| **1.3.0** | 2024-04-01 | Mobile responsive design |

---

*This documentation is maintained by the Retail Management System team. For updates or corrections, please submit a pull request or contact the development team.*

**Last Updated**: January 2024
**Document Version**: 1.0.0
