# Retail Management System — Comprehensive Documentation

## Table of Contents
1. System Overview
2. Architecture & Technology Stack
3. Applications & Modules
4. Data Model Overview
5. Roles, Authentication & Authorization
6. Core Workflows
7. Frontend & Navigation
8. Import/Export & Timezone
9. Installation & Setup
10. Configuration
11. Running & Management Commands
12. Testing & Sample Data
13. Deployment Notes
14. Security Practices
15. Production Readiness Assessment
16. Security Audit & Penetration Testing
17. Troubleshooting

---

## 1) System Overview
A Django-based multi-app system for managing retail operations across stores, inventory, procurement, HR, sales, reporting, and e-commerce. It ships with Bootstrap templates, a shared base layout, and per-app UIs. The default DB is SQLite for development.

Key capabilities:
- Multi-store operations with Store as a first-class entity
- Inventory: products, brands, categories, store-specific inventory, stock movements
- Procurement: suppliers, purchase orders, receiving
- HR: employees, attendance, payroll
- Sales: sales transactions and customer orders
- E-commerce: product browse and online orders
- Reporting and dashboards

---

## 2) Architecture & Technology Stack

Backend
- Django 5.2.4 (Python 3.13 runtime)
- Database: SQLite (development), PostgreSQL (production-ready)
- Security: Cryptography, SSL/TLS support
- Monitoring: psutil for system monitoring
- File Processing: python-magic for secure file handling
- Data Processing: pandas, openpyxl for exports
- Testing: pytest, pytest-django
- Development: django-extensions, django-debug-toolbar

Frontend
- Django templates with Bootstrap 5.1.3
- Font Awesome 6.0.0 icons
- Custom CSS/JS under /static and collected /staticfiles
- Responsive design with Bootstrap components

Project layout (key paths)
- Project settings: retail_management_system/settings.py
- Project URLs: retail_management_system/urls.py
- Base template: templates/base.html
- Apps: accounts, inventory, procurement, sales, store_management, human_resources, reporting, e_commerce, dashboards, api
- Middleware: Custom security, logging, file upload restrictions
- Logs: Comprehensive logging (security, audit, performance, error)

Notes
- API framework ready (api/ app exists, DRF not yet implemented)
- Production database migration to PostgreSQL completed
- SSL/TLS certificates and HTTPS configuration available
- Security scanning and penetration testing tools integrated

---

## 3) Applications & Modules

accounts
- Authentication extensions and login templates in templates/registration/* (staff, customer flows)

inventory
- Models: Category, Brand, Product, StoreInventory, StockMovement (planned/used by flows)
- URLs: product_list/create/detail/edit/delete; brand_list; category_list; stock_movement_list; storeinventory_list
- Features: CRUD for products, brands, categories; store-level inventory; movements

procurement
- Models: Supplier, SupplierProduct, PurchaseOrder, PurchaseOrderItem
- URLs: supplier_*, supplierproduct_*, purchaseorder_* (list/detail/create/update/delete), purchaseorder_status, purchaseorder_receive
- Features: supplier management, PO lifecycle, receiving; integration point to increment store inventory on receive

store_management
- Provides Store model and CRUD; store-level settings and navigation entry

human_resources
- Models: Employee, Attendance, Payroll
- URLs: employee_list/create, attendance_list, payroll_list, exports
- Features: attendance tracking, payroll management, CSV exports

sales
- SalesTransaction, CustomerOrder (as per URLs/templates)
- URLs: sales_transaction_list, customer_order_list

reporting
- Reporting pages and dashboards per app

e_commerce
- Customer-facing browsing and order constructs
- URLs: product_browse, online_order_list, customer_account_list

dashboards
- Root dashboard at dashboards:dashboard

---

## 4) Data Model Overview

Core relationships (high-level):
- Store 1—* StoreInventory (*per Product per Store*)
- Product *—1 Brand, Product *—1 Category
- StockMovement tracks quantity deltas per Product per Store (planned/used)
- Supplier 1—* PurchaseOrder 1—* PurchaseOrderItem (references Product)
- Employee has Attendance and Payroll entries
- SalesTransaction and CustomerOrder reference products/items (via app logic)

Planned/important constraints
- StoreInventory: unique (store, product)
- StockMovement: records type (inbound/outbound/adjustment) and quantities

---

## 5) Roles, Authentication & Authorization

Roles observed in UI and templates
- Staff (default back-office users)
- Customer (limited navigation; separate login/registration screens)

Permissions and visibility
- Landing page ('/') is accessible to anonymous users without login
- Base navigation hides most management menus for user.is_customer
- Staff get access to Stores, HR, Inventory, Procurement, Analytics
- Customers see e-commerce options (browse, online orders, account) and Sales menu entries relevant to them

Authentication templates
- templates/registration/login.html, staff_login.html, customer_login.html, customer_registration.html, logout.html

---

## 6) Core Workflows

Inventory workflow
1. Create Category/Brand
2. Create Product
3. Initialize StoreInventory (per store)
4. Record StockMovements for adjustments/transfers

Procurement workflow
1. Create Supplier and SupplierProduct
2. Create Purchase Order with items
3. Update PO status and Receive goods
4. Receiving should increment StoreInventory and log inbound StockMovement (planned/implemented per views)

HR workflow
1. Create Employee
2. Track Attendance
3. Process Payroll
4. Export CSVs where needed

Sales workflow
1. Record SalesTransaction
2. Manage CustomerOrder
3. Reporting pulls sales analytics

E-commerce workflow
1. Browse Products
2. Place Online Orders
3. Manage Customer Accounts

---

## 7) Frontend & Navigation

Base template: templates/base.html
- Bootstrap 5, Font Awesome, custom main.css, main.js
- Navbar links conditionally rendered by user role
- Menus:
  - Stores: list/create
  - HR: employees, attendance, payroll, exports
  - Inventory: products, brands, categories, stock movement, store inventory
  - Sales: transactions, customer orders
  - Ecommerce: browse, online orders, customer accounts
  - Procurement: suppliers, purchase orders, create PO
  - Analytics: analytics:dashboard (visible to staff)

Shared includes
- templates/includes/pagination.html

---

## 8) Import/Export & Timezone

Exports (HR examples seen in nav)
- Employees CSV: hr:employee_export?format=csv
- Attendance CSV: hr:attendance_export?format=csv
- Payroll CSV: hr:payroll_export?format=csv

Timezone considerations
- See EXPORT_TIMEZONE_FIX.md for known adjustments and best practices (ensure timezone-aware datetimes when exporting; align with USE_TZ in settings).

---

## 9) Installation & Setup

Prerequisites
- Python 3.11+ (project compiled with 3.13 locally; Python 3.10+ recommended)
- pip

Steps
1. Create and activate a virtual environment
   - Windows PowerShell
     ```powershell
     python -m venv env
     .\env\Scripts\Activate.ps1
     ```
   - macOS/Linux
     ```bash
     python -m venv env
     source env/bin/activate
     ```
2. Install Django (requirements.txt may be absent)
   ```bash
   pip install django
   ```
3. Apply migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```
5. Run the server
   ```bash
   python manage.py runserver
   ```

Default DB
- SQLite file db.sqlite3 is included/created locally; no external DB setup required for development.

Static/Media
- Development uses /static and /media directories
- For production, configure STATIC_ROOT and MEDIA_ROOT; run collectstatic

---

## 10) Configuration

Key settings (retail_management_system/settings.py)
- Installed apps include: accounts, inventory, procurement, sales, store_management, human_resources, reporting, e_commerce, dashboards
- Templates directory includes /templates with base.html
- Static files served from /static; collected into /staticfiles in production
- Authentication templates under templates/registration

Environment
- For production, set DEBUG=False, ALLOWED_HOSTS, DATABASES, STATIC_ROOT, MEDIA_ROOT

---

## 11) Running & Management Commands

Common commands
- runserver: start dev server
- makemigrations/migrate: schema management
- createsuperuser: admin login

Helper scripts in repo (optional utilities)
- create_test_data.py, populate_inventory.py, populate_stores.py
- create_test_staff_users.py, create_test_customer_users.py, create_superuser.py
- check_product_images.py, assign_images_to_products.py
- add_inventory_to_products.py
- reset.py
- diagnose_teststaff3.py
- populate_ecommerce_products.py

Run a script
```bash
python script_name.py
```
Note: Some scripts may assume existing data or paths; review each file before running.

---

## 12) Testing & Sample Data

Tests present
- tests within app folders (e.g., store_management/tests.py)
- top-level quick scripts for smoke testing login, product creation, relationships:
  - test_staff_login.py, test_customer_login.py, test_customer_login_verification.py, test_product_creation.py, test_manager_relationships.py

Suggested flow
1. Run migrations and create superuser
2. Use populate_* scripts to seed minimal data
3. Log in as staff and explore Inventory/Procurement/HR flows
4. Log in as customer and verify e-commerce navigation and restrictions

---

## 13) Deployment Notes

Baseline
- Use a production-grade DB (e.g., PostgreSQL) if needed
- Configure SECRET_KEY, DEBUG=False, ALLOWED_HOSTS
- Configure STATIC_ROOT and run `python manage.py collectstatic`
- Serve via WSGI (gunicorn/uwsgi + reverse proxy) or a PaaS with Django support

Data & media
- Persist MEDIA_ROOT on durable storage

Migrations
- Run migrations on deploy; apply data migrations as required

---

## 14) Security Practices

Core Security Features:
- CSRF enabled for all forms
- Django ORM for SQL injection protection
- Auto-escaping templates for XSS reduction
- Use LoginRequired on management views; staff-only where applicable
- Strong passwords and per-user roles; never commit secrets
- For production: HTTPS, secure session/cookie settings, HSTS at proxy layer

Advanced Security Features:
- Custom middleware: CustomerRestrictionMiddleware, SecureFileUploadMiddleware, logging_middleware
- SSL/TLS certificate generation and testing scripts
- Security scanning tools: penetration_test_suite.py, security_scanner.py
- Comprehensive logging: security.log, audit.log, performance.log, error.log
- File upload security with python-magic for type validation
- Environment-based configuration for sensitive settings
- Argon2 password hashing with strong validation (12+ characters)
- Session security with timeout and concurrent session control

Security Testing:
- Automated penetration testing suite
- Manual security audit checklist
- OWASP ZAP, Nikto, SQLMap, Nmap integration
- SSL/TLS configuration testing
- Database security assessment

See SECURITY_PROTOCOLS.md and SECURITY_AUDIT_PENETRATION_TESTING_PLAN.md for expanded guidelines.


---

## 15) Troubleshooting

Common issues
- Cannot log in: ensure migrations applied and superuser created
- Missing menus: user might be a customer; staff menus hidden for is_customer
- Static not loading (dev): check DEBUG=True and STATIC_URL; (prod) run collectstatic and serve via web server
- Timezone mismatch in exports: confirm USE_TZ=True and follow EXPORT_TIMEZONE_FIX.md
- Inventory totals incorrect: verify StoreInventory exists for each product/store and StockMovements applied

Where to look
- BASE_HTML_IMPROVEMENTS.md for UI/nav improvements context
- ATTENDANCE_FORM_IMPROVEMENTS.md, STORE_FORM_IMPROVEMENTS.md for feature-specific notes
- SYSTEM_DOCUMENTATION.md and SYSTEM_FILE_HIERARCHY.md for broader reference

---

## 16) Production Readiness Assessment

See PRODUCTION_READINESS_ASSESSMENT.md for full details.

Summary:
- Current status: Limited testing completed; not fully ready for production.
- Database: PostgreSQL configured; migration completed.
- Security: Production security settings implemented; SSL/TLS verified.
- Static files: Production static file configuration in place.
- Testing: Partial testing completed; some issues with DB conflicts.
- Deployment: No verified deployment strategy; needs containerization or cloud deployment.
- Immediate next steps: Database migration verification, security hardening, static files setup, comprehensive testing, deployment preparation.

---

## 17) Security Audit & Penetration Testing

See SECURITY_AUDIT_PENETRATION_TESTING_PLAN.md for full details.

Summary:
- Comprehensive manual and automated security testing plan.
- Covers authentication, authorization, input validation, session management, file upload, API, and network security.
- Includes test cases for brute force, SQL injection, XSS, CSRF, privilege escalation, and more.
- Automated tools: OWASP ZAP, Nikto, SQLMap, Nmap, SSLScan.
- Recommendations: Implement automated testing, enhance monitoring, strengthen authentication, improve API and database security.
- Implementation timeline: Immediate to long-term phases with clear milestones.
- Success metrics and risk assessment included.

---

Last updated: September 2025 - Updated to reflect current repository state with PostgreSQL support, advanced security features, SSL/TLS configuration, and production readiness assessment.
