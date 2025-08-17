# Retail Management System — Repo Overview

## Stack
- Framework: Django
- DB: SQLite (db.sqlite3)
- Python entrypoints: manage.py, asgi.py, wsgi.py
- Apps: inventory, procurement, sales, store_management, human_resources, reporting, e_commerce
- Templates: project-wide in /templates and app-scoped templates under each app
- Static: /static and collected /staticfiles

## Key Apps and Features

### inventory
- Models: Category, Brand, Product, StoreInventory
- Views: CRUD for Product (list, detail, create, update, delete)
- URLs (namespace: inventory): product_list, product_create, product_detail, product_edit, product_delete
- Templates: inventory/product_*.html
- TODO: Stock movements, stock adjustments, stock list per store

### procurement
- Models: Supplier, SupplierProduct, PurchaseOrder, PurchaseOrderItem
- Views: Supplier CRUD; SupplierProduct add/update/delete; Purchase Order list/detail/create/update/delete; status transitions; receive flow
- URLs (namespace: procurement): supplier_*, supplierproduct_*, purchaseorder_*, purchaseorder_status, purchaseorder_receive
- Templates: procurement/supplier_*.html, procurement/purchaseorder_*.html

### store_management
- Provides Store model used by inventory and procurement

### human_resources
- Provides Employee and related HR features (attendance etc.)

### sales
- Sales domain (hooks for future stock decrement on sales)

### reporting
- Reporting pages (not directly coupled to stock yet)

## Common Paths
- Project settings: retail_management_system/settings.py
- Project URLs: retail_management_system/urls.py
- Base template: templates/base.html

## Developer Tasks
1) Setup
- Create and activate a virtualenv
- Install dependencies (requirements.txt not present in repo listing; install Django if needed):
  - pip install django

2) Migrations
- python manage.py makemigrations
- python manage.py migrate

3) Runserver
- python manage.py runserver

4) Create superuser (to access Django admin)
- python manage.py createsuperuser

## Notes
- Procurement suppliers should be reused by Inventory for sourcing.
- StoreInventory tracks quantity per product per store (unique constraint).
- Planned: StockMovement model, manual adjustments, integration where receiving Purchase Orders increments StoreInventory. Sales integration to decrement stock can be added later.

## Conventions
- Bootstrap-based templates extending templates/base.html
- LoginRequiredMixin on most views

## Tips
- For low-stock alerts, compare StoreInventory.quantity <= StoreInventory.reorder_level
- For PO receiving, compute delta between previously received and new received quantity, and create an inbound stock movement for the delta.