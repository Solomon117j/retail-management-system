# Permission System Guide

This guide explains how to use the comprehensive permission system implemented in the retail management system.

## Overview

The permission system is organized into:
1. **Functional Area Groups** - Permissions grouped by business function
2. **Role-Based Groups** - Job titles with specific permission combinations
3. **Individual Permissions** - Granular access control

## Available Roles

### Store Manager
- **Full Access**: All permissions across all modules
- **Use Case**: Store owners, general managers

### Assistant Manager
- **Limited Management**: Most permissions except critical settings
- **Exclusions**: `manage_store_settings`, `approve_purchase_orders`
- **Use Case**: Deputy managers, shift supervisors

### Inventory Supervisor
- **Inventory Focus**: Full inventory management + basic sales
- **Additional**: Can process sales and receive stock
- **Use Case**: Warehouse managers, inventory specialists

### Sales Associate
- **Sales Focus**: Sales transactions + basic inventory viewing
- **Use Case**: Cashiers, sales floor staff

### Procurement Specialist
- **Procurement Focus**: Purchase orders, suppliers, stock receiving
- **Use Case**: Buyers, procurement officers

### HR Coordinator
- **HR Focus**: Employee management, attendance, payroll
- **Use Case**: HR staff, office managers

### E-Commerce Manager
- **Online Focus**: E-commerce operations + inventory management
- **Use Case**: Online store managers, digital marketing staff

### Financial Analyst
- **Reporting Focus**: Financial reports and business analytics
- **Use Case**: Accountants, business analysts

### System Administrator
- **Technical Focus**: System settings, integrations, audit logs
- **Use Case**: IT staff, system administrators

## Management Commands

### Setup Permission Groups
```bash
python manage.py setup_permissions --create-groups
```
Creates functional area groups (StoreManagement, Inventory, Sales, etc.)

### Setup Role Groups
```bash
python manage.py setup_permissions --create-roles
```
Creates role-based groups with specific permission combinations.

### Assign Role to User
```bash
python manage.py setup_permissions --assign-role "Sales Associate" --username "john_doe"
```
Assigns a role to a specific user and updates their position field.

### List Role Permissions
```bash
python manage.py setup_permissions --list-permissions "Sales Associate"
```
Shows all permissions for a specific role.

## Using Permissions in Views

### Method 1: Permission Mixin (Class-Based Views)
```python
from human_resources.permissions import PermissionMixin

class ProductListView(PermissionMixin, LoginRequiredMixin, ListView):
    model = Product
    required_permission = 'view_inventory'
    permission_denied_message = "You don't have permission to view inventory."
    permission_denied_url = 'dashboards:dashboard'
```

### Method 2: Permission Decorators (Function-Based Views)
```python
from human_resources.permissions import require_permission

@require_permission('view_inventory')
def inventory_list(request):
    # View logic here
    pass
```

### Method 3: Multiple Permissions
```python
# Require ANY of the permissions
@require_any_permission('view_inventory', 'access_inventory')
def inventory_dashboard(request):
    pass

# Require ALL permissions
@require_all_permissions('edit_inventory', 'manage_inventory_categories')
def advanced_inventory_edit(request):
    pass
```

### Method 4: Custom Permission Checking
```python
from human_resources.permissions import has_permission

def my_view(request):
    if has_permission(request.user, 'edit_inventory'):
        # User can edit
        pass
    else:
        # User cannot edit
        pass
```

## Using Permissions in Templates

### Check Single Permission
```html
{% if perms.human_resources.view_inventory %}
    <a href="{% url 'inventory:product_list' %}">View Products</a>
{% endif %}
```

### Check Multiple Permissions
```html
{% if perms.human_resources.edit_inventory %}
    <a href="{% url 'inventory:product_create' %}" class="btn btn-success">Add Product</a>
    <a href="{% url 'inventory:product_update' product.pk %}" class="btn btn-primary">Edit</a>
{% endif %}
```

### Conditional Content
```html
<table class="table">
    <thead>
        <tr>
            <th>Product</th>
            <th>Price</th>
            {% if perms.human_resources.edit_inventory %}
                <th>Actions</th>
            {% endif %}
        </tr>
    </thead>
    <!-- ... -->
</table>
```

## Permission List

### Store Management
- `view_store_dashboard` - Can view store management dashboard
- `manage_store_settings` - Can modify store configuration and settings
- `manage_departments` - Can create/edit/delete store departments

### Inventory
- `access_inventory` - Can access inventory management system
- `view_inventory` - Can view inventory items and stock levels
- `edit_inventory` - Can modify inventory items and quantities
- `manage_inventory_categories` - Can organize inventory categories
- `perform_inventory_audit` - Can conduct physical inventory counts

### Sales
- `process_sales` - Can process in-store sales transactions
- `void_sales` - Can void/completely cancel sales transactions
- `manage_sales_promotions` - Can configure sales promotions/discounts
- `view_sales_reports` - Can access sales performance reports

### Procurement
- `create_purchase_orders` - Can generate new procurement orders
- `approve_purchase_orders` - Can authorize procurement requests
- `manage_suppliers` - Can maintain supplier/vendor records
- `receive_stock` - Can process received shipments

### Human Resources
- `view_employee_directory` - Can access employee contact information
- `manage_employee_records` - Can maintain HR records (excluding sensitive data)
- `access_hr_reports` - Can view HR analytics and reports
- `manage_recruitment` - Can handle hiring processes

### E-Commerce
- `manage_online_listings` - Can maintain e-commerce product listings
- `process_online_orders` - Can fulfill e-commerce purchases
- `handle_customer_portals` - Can manage customer account portals
- `view_web_analytics` - Can access e-commerce traffic/revenue reports

### Reporting
- `generate_financial_reports` - Can create financial statements
- `export_data_reports` - Can export datasets for external analysis
- `access_executive_dashboards` - Can view strategic business dashboards
- `schedule_automated_reports` - Can configure report automation

### Cross-Module
- `override_inventory_checks` - Can bypass inventory validation rules
- `access_audit_logs` - Can view system audit trails
- `manage_api_integrations` - Can configure system integrations

## Best Practices

1. **Use Role-Based Groups**: Assign users to role groups rather than individual permissions
2. **Principle of Least Privilege**: Give users only the permissions they need
3. **Regular Audits**: Periodically review user permissions and roles
4. **Template Permissions**: Always check permissions in templates before showing actions
5. **Graceful Degradation**: Provide meaningful error messages when permissions are denied

## Troubleshooting

### Permission Not Working
1. Check if the permission exists in the database
2. Verify the user is in the correct group
3. Ensure the permission codename is correct
4. Check if the user is active

### Role Assignment Issues
1. Make sure role groups are created first (`--create-roles`)
2. Verify the username exists
3. Check the role name spelling

### Template Permission Issues
1. Use the full permission path: `perms.human_resources.permission_name`
2. Ensure the user is authenticated
3. Check if the permission is assigned to the user or their groups