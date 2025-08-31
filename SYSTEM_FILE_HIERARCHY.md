# Retail Management System - Complete File Hierarchy

## Project Root Structure
```
retail_management_system/
├── manage.py                          # Django management script
├── db.sqlite3                         # SQLite database file
├── requirements.txt                   # Python dependencies
├── asgi.py                           # ASGI configuration
├── reset.py                          # Database reset utility
├── populate_inventory.py             # Data population script
├── test_product_creation.py          # Testing script
├── TODO.md                           # Development tasks
│
├── retail_management_system/         # Main project configuration
│   ├── __init__.py
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # Main URL configuration
│   ├── wsgi.py                       # WSGI configuration
│   ├── middleware.py                 # Custom middleware
│   └── views.py                      # Project-level views
│
├── templates/                        # Global templates
│   ├── base.html                     # Base template
│   ├── delete_confirm.html           # Delete confirmation template
│   ├── dashboard/
│   │   └── index.html                # Dashboard template
│   ├── registration/
│   │   ├── login.html                # Login template
│   │   ├── customer_login.html       # Customer login template
│   │   ├── staff_login.html          # Staff login template
│   │   ├── login_choice.html         # Login choice template
│   │   ├── customer_registration.html # Customer registration template
│   │   └── logout.html               # Logout template
│   └── includes/
│       └── pagination.html           # Pagination component
│
├── static/                           # Global static files
│   ├── css/
│   │   └── main.css                  # Main stylesheet
│   ├── js/
│   │   └── main.js                   # Main JavaScript
│   └── images/
│       └── art.jpeg                  # System images
│
├── staticfiles/                      # Collected static files (production)
│
├── media/                            # Media files (user uploads)
│   └── employee_profiles/            # Employee profile images
│
├── Documentation/                    # Project documentation
│   ├── SYSTEM_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── RETAIL_MANAGEMENT_SYSTEM_COMPREHENSIVE_DOCUMENTATION.md
│   ├── SYSTEM_FILE_HIERARCHY.md
│   ├── SECURITY_PROTOCOLS.md
│   ├── PERMISSIONS_GUIDE.md
│   ├── EMPLOYEE_MANAGEMENT_COMPLETE.md
│   ├── PAYROLL_VIEWS_COMPLETE.md
│   ├── SHARED_STYLES_GUIDE.md
│   ├── BASE_HTML_IMPROVEMENTS.md
│   ├── STORE_FORM_IMPROVEMENTS.md
│   ├── ATTENDANCE_FORM_IMPROVEMENTS.md
│   ├── EXPORT_TIMEZONE_FIX.md
│   ├── HOW_TO_ACCESS_PAYROLL.md
│   └── SYSTEM_FLOWCHARTS.md
│
├── accounts/                         # Authentication & User Management
│   ├── __init__.py
│   ├── admin.py                      # Admin configuration
│   ├── apps.py                       # App configuration
│   ├── models.py                     # User models
│   ├── signals.py                    # Signal handlers
│   ├── tests.py                      # Test cases
│   ├── urls.py                       # URL patterns
│   ├── views.py                      # View functions
│   └── migrations/                   # Database migrations
│       ├── __init__.py
│       ├── 0001_initial.py
│       └── 0002_alter_customer_id_alter_employee_id_alter_user_id.py
│
├── dashboards/                       # Dashboard Application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/dashboards/
│
├── human_resources/                  # HR Management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                      # HR forms
│   ├── models.py                     # Employee, Attendance, Payroll models
│   ├── permissions.py                # Permission classes
│   ├── signals.py                    # Signal handlers
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/                 # Management commands
│   ├── migrations/                   # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_employee_store.py
│   │   ├── 0003_payroll_attendance.py
│   │   └── 0004_employee_profile_image_alter_attendance_employee_and_more.py
│   ├── static/human_resources/       # HR static files
│   ├── templates/human_resources/    # HR templates
│   └── templatetags/                 # Custom template tags
│       ├── __init__.py
│       └── attendance_filters.py
│
├── inventory/                        # Inventory Management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                      # Inventory forms
│   ├── models.py                     # Product, Category, Brand models
│   ├── tests.py
│   ├── urls.py
│   ├── views_with_permissions.py     # Permission-based views
│   ├── views.py                      # Main views
│   ├── migrations/                   # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── 0002_stockmovement.py
│   ├── static/inventory/             # Inventory static files
│   └── templates/inventory/          # Inventory templates
│
├── procurement/                      # Procurement Management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                     # Supplier, PurchaseOrder models
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/                   # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_supplier_is_active.py
│   │   └── 0003_alter_purchaseorder_created_by.py
│   └── templates/procurement/        # Procurement templates
│
├── reporting/                        # Analytics & Reporting
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                     # Report models
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/                   # Database migrations
│   │   └── __init__.py
│   └── templates/reporting/          # Reporting templates
│
├── sales/                            # Sales Management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                     # Sale, SaleItem models
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/                   # Database migrations
│   └── templates/sales/              # Sales templates
│
├── store_management/                 # Store Management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                      # Store forms
│   ├── models.py                     # Store, Department models
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/                   # Database migrations
│   ├── static/store_management/      # Store static files
│   └── templates/store_management/   # Store templates
│
├── e_commerce/                       # E-Commerce Module
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── mixins.py                     # Mixin classes
│   ├── models.py                     # Order, Customer models
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/                   # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_customeraccount.py
│   │   ├── 0003_alter_customeraccount_options_and_more.py
│   │   └── 0004_alter_customeraccount_id_alter_onlineorder_id_and_more.py
│   ├── static/e_commerce/            # E-commerce static files
│   └── templates/e_commerce/         # E-commerce templates
│
└── templatetags/                     # Global template tags
    ├── __init__.py
    └── attendance_filters.py
```

## Key Configuration Files

### settings.py (Main Configuration)
- Database configuration (SQLite/PostgreSQL)
- Installed apps list
- Middleware configuration
- Static files settings
- Authentication settings
- Internationalization
- Security settings

### urls.py (URL Routing)
- Main project URL patterns
- App URL includes
- Admin panel URLs
- API endpoints

### models.py (per app)
- Database schema definitions
- Model relationships
- Business logic methods
- Custom managers and querysets

## Static Files Structure
```
static/
├── css/
│   └── main.css                      # Main stylesheet with Bootstrap customization
├── js/
│   └── main.js                       # Main JavaScript functionality
└── images/
    └── art.jpeg                      # System branding images

staticfiles/                          # Production collected static files
├── admin/                            # Django admin static files
├── css/                              # Compiled CSS
├── debug_toolbar/                    # Debug toolbar assets
├── django_extensions/                # Django extensions assets
├── human_resources/                  # HR app static files
├── inventory/                        # Inventory app static files
├── js/                               # Compiled JavaScript
└── store_management/                 # Store management static files
```

## Template Structure
```
templates/
├── base.html                         # Base template with navigation
├── delete_confirm.html               # Delete confirmation modal
├── dashboard/
│   └── index.html                    # Main dashboard
├── registration/                     # Authentication templates
│   ├── login.html                    # Generic login
│   ├── customer_login.html           # Customer login
│   ├── staff_login.html              # Staff login
│   ├── login_choice.html             # Login type selection
│   ├── customer_registration.html    # Customer registration
│   └── logout.html                   # Logout confirmation
└── includes/
    └── pagination.html               # Pagination component
```

## Database Structure
- **SQLite** for development (db.sqlite3)
- **PostgreSQL** ready for production
- **Migrations** tracked per app
- **Media files** stored in media/ directory

## Development Utilities
- `reset.py` - Database reset script
- `populate_inventory.py` - Test data generation
- `test_product_creation.py` - Product testing
- Various test scripts for user creation and verification

## Documentation Files
Comprehensive documentation covering:
- System architecture and design
- Database schema and relationships
- Security protocols and permissions
- Employee management workflows
- Payroll processing
- Style guides and UI improvements
- System flowcharts and processes

This file hierarchy represents a well-structured Django project following best practices with modular app design, proper separation of concerns, and comprehensive documentation.
