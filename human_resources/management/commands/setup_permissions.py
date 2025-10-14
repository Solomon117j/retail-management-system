from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from human_resources.models import Employee


class Command(BaseCommand):
    help = 'Set up permission groups and roles for the retail management system'

    # Grouped Permissions by Functional Area
    permission_groups = {
        "StoreManagement": [
            ("view_store_dashboard", "Can view store management dashboard"),
            ("manage_store_settings", "Can modify store configuration and settings"),
            ("manage_departments", "Can create/edit/delete store departments"),
        ],

        "Sales": [
            ("process_sales", "Can process in-store sales transactions"),
            ("void_sales", "Can void/completely cancel sales transactions"),
            ("manage_sales_promotions", "Can configure sales promotions/discounts"),
            ("view_sales_reports", "Can access sales performance reports"),
        ],
        "Procurement": [
            ("create_purchase_orders", "Can generate new procurement orders"),
            ("approve_purchase_orders", "Can authorize procurement requests"),
            ("manage_suppliers", "Can maintain supplier/vendor records"),
            ("receive_stock", "Can process received shipments"),
        ],
        "HumanResources": [
            ("view_employee_directory", "Can access employee contact information"),
            ("manage_employee_records", "Can maintain HR records (excluding sensitive data)"),
            ("access_hr_reports", "Can view HR analytics and reports"),
            ("manage_recruitment", "Can handle hiring processes"),
        ],
        "ECommerce": [
            ("manage_online_listings", "Can maintain e-commerce product listings"),
            ("process_online_orders", "Can fulfill e-commerce purchases"),
            ("handle_customer_portals", "Can manage customer account portals"),
            ("view_web_analytics", "Can access e-commerce traffic/revenue reports"),
        ],
        "Reporting": [
            ("generate_financial_reports", "Can create financial statements"),
            ("export_data_reports", "Can export datasets for external analysis"),
            ("access_executive_dashboards", "Can view strategic business dashboards"),
            ("schedule_automated_reports", "Can configure report automation"),
        ],
        "Cross-Module": [
            ("override_inventory_checks", "Can bypass inventory validation rules"),
            ("access_audit_logs", "Can view system audit trails"),
            ("manage_api_integrations", "Can configure system integrations"),
        ]
    }

    # Job Titles with Permission Groups and Specific Adjustments
    role_permissions = {
        "Store Manager": {
            "groups": ["StoreManagement", "Sales", "Procurement",
                      "HumanResources", "ECommerce", "Reporting", "Cross-Module"],
            "additional_permissions": []
        },
        "Assistant Manager": {
            "groups": ["StoreManagement", "Sales", "Procurement", "ECommerce"],
            "exclusions": ["manage_store_settings", "approve_purchase_orders"],
            "additional_permissions": ["view_sales_reports", "access_hr_reports"]
        },
        "Inventory Supervisor": {
            "groups": ["Inventory"],
            "additional_permissions": ["process_sales", "void_sales", "receive_stock"]
        },
        "Sales Associate": {
            "groups": ["Sales"],
            "additional_permissions": ["access_inventory", "view_inventory"]
        },
        "Procurement Specialist": {
            "groups": ["Procurement"],
            "additional_permissions": ["access_inventory", "manage_suppliers"]
        },
        "HR Coordinator": {
            "groups": ["HumanResources"],
            "additional_permissions": ["view_store_dashboard"]
        },
        "E-Commerce Manager": {
            "groups": ["ECommerce", "Inventory"],
            "additional_permissions": ["view_sales_reports", "view_web_analytics"]
        },
        "Financial Analyst": {
            "groups": ["Reporting"],
            "additional_permissions": ["generate_financial_reports", "access_executive_dashboards"]
        },
        "System Administrator": {
            "groups": ["Cross-Module"],
            "additional_permissions": ["manage_store_settings", "access_audit_logs"]
        }
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-groups',
            action='store_true',
            help='Create permission groups based on functional areas',
        )
        parser.add_argument(
            '--create-roles',
            action='store_true',
            help='Create role-based groups with specific permissions',
        )
        parser.add_argument(
            '--assign-role',
            type=str,
            help='Assign a role to a user by username',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for role assignment',
        )
        parser.add_argument(
            '--list-permissions',
            type=str,
            help='List permissions for a specific role',
        )

    def handle(self, *args, **options):
        if options['create_groups']:
            self.create_permission_groups()
        
        if options['create_roles']:
            self.create_role_groups()
        
        if options['assign_role'] and options['username']:
            self.assign_role_to_user(options['username'], options['assign_role'])
        
        if options['list_permissions']:
            self.list_role_permissions(options['list_permissions'])

    def create_permission_groups(self):
        """Create groups based on functional areas"""
        self.stdout.write(self.style.SUCCESS('Creating functional area permission groups...'))
        
        employee_content_type = ContentType.objects.get_for_model(Employee)
        
        for group_name, permissions in self.permission_groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(f'Created group: {group_name}')
            else:
                self.stdout.write(f'Group already exists: {group_name}')
            
            # Clear existing permissions and add new ones
            group.permissions.clear()
            
            for perm_codename, perm_name in permissions:
                try:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=employee_content_type
                    )
                    group.permissions.add(permission)
                    self.stdout.write(f'  Added permission: {perm_codename}')
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  Permission not found: {perm_codename}')
                    )

    def create_role_groups(self):
        """Create role-based groups with specific permission combinations"""
        self.stdout.write(self.style.SUCCESS('Creating role-based permission groups...'))
        
        employee_content_type = ContentType.objects.get_for_model(Employee)
        
        for role_name, role_config in self.role_permissions.items():
            group, created = Group.objects.get_or_create(name=f"Role: {role_name}")
            
            if created:
                self.stdout.write(f'Created role group: {role_name}')
            else:
                self.stdout.write(f'Role group already exists: {role_name}')
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Get permissions for this role
            permissions = self.get_permissions_for_role(role_name)
            
            for perm_codename, perm_name in permissions:
                try:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=employee_content_type
                    )
                    group.permissions.add(permission)
                    self.stdout.write(f'  Added permission: {perm_codename}')
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  Permission not found: {perm_codename}')
                    )

    def get_permissions_for_role(self, role_name):
        """Helper function to resolve permissions for a role"""
        if role_name not in self.role_permissions:
            return []
        
        role = self.role_permissions[role_name]
        permissions = []
        
        # Add group permissions
        for group in role["groups"]:
            permissions.extend(self.permission_groups.get(group, []))
        
        # Add individual permissions
        for perm_codename in role.get("additional_permissions", []):
            # Search through all groups to find the permission
            for group_perms in self.permission_groups.values():
                for perm in group_perms:
                    if perm[0] == perm_codename:
                        permissions.append(perm)
                        break
        
        # Remove exclusions if defined
        exclusions = role.get("exclusions", [])
        permissions = [p for p in permissions if p[0] not in exclusions]
        
        return list(set(permissions))  # Remove duplicates

    def assign_role_to_user(self, username, role_name):
        """Assign a role to a specific user"""
        try:
            user = Employee.objects.get(username=username)
            role_group_name = f"Role: {role_name}"
            
            try:
                role_group = Group.objects.get(name=role_group_name)
                user.groups.add(role_group)
                user.position = role_name  # Update the position field
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Assigned role "{role_name}" to user "{username}"')
                )
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Role group "{role_group_name}" does not exist. Run --create-roles first.')
                )
        except Employee.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist.')
            )

    def list_role_permissions(self, role_name):
        """List all permissions for a specific role"""
        if role_name not in self.role_permissions:
            self.stdout.write(
                self.style.ERROR(f'Role "{role_name}" is not defined.')
            )
            return
        
        permissions = self.get_permissions_for_role(role_name)
        
        self.stdout.write(self.style.SUCCESS(f'Permissions for role: {role_name}'))
        self.stdout.write('-' * 50)
        
        for perm_codename, perm_name in permissions:
            self.stdout.write(f'  {perm_codename}: {perm_name}')
        
        self.stdout.write(f'\nTotal permissions: {len(permissions)}')