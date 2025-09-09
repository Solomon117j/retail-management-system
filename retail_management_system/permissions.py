"""
Enhanced Role-Based Access Control System for Retail Management System

This module provides:
- Custom permission decorators for function-based views
- Permission mixins for class-based views
- Role-based access control utilities
- Hierarchical role system
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from typing import List, Union, Optional
import logging

logger = logging.getLogger(__name__)

# Role Hierarchy Definition
ROLE_HIERARCHY = {
    'superuser': 100,  # Full system access
    'manager': 80,     # Store/department management
    'hr_manager': 70,  # HR and payroll management
    'inventory_manager': 60,  # Inventory management
    'sales_person': 50,  # Sales processing
    'staff': 40,       # General staff access
    'customer': 10,    # Customer access only
}

# Permission Groups
PERMISSION_GROUPS = {
    'store_management': [
        'store_management.view_store_dashboard',
        'store_management.manage_store_settings',
        'store_management.manage_departments',
    ],
    'inventory': [
        'inventory.access_inventory',
        'inventory.view_inventory',
        'inventory.edit_inventory',
        'inventory.manage_inventory_categories',
        'inventory.perform_inventory_audit',
    ],
    'sales': [
        'sales.process_sales',
        'sales.void_sales',
        'sales.manage_sales_promotions',
        'sales.view_sales_reports',
    ],
    'procurement': [
        'procurement.create_purchase_orders',
        'procurement.approve_purchase_orders',
        'procurement.manage_suppliers',
        'procurement.receive_stock',
    ],
    'human_resources': [
        'human_resources.view_employee_directory',
        'human_resources.manage_employee_records',
        'human_resources.access_hr_reports',
        'human_resources.manage_recruitment',
    ],
    'e_commerce': [
        'e_commerce.manage_online_listings',
        'e_commerce.process_online_orders',
        'e_commerce.handle_customer_portals',
        'e_commerce.view_web_analytics',
    ],
    'reporting': [
        'reporting.generate_financial_reports',
        'reporting.export_data_reports',
        'reporting.access_executive_dashboards',
        'reporting.schedule_automated_reports',
    ],
    'cross_module': [
        'override_inventory_checks',
        'access_audit_logs',
        'manage_api_integrations',
    ]
}


class PermissionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for class-based views that require specific permissions.

    Usage:
        class MyView(PermissionRequiredMixin, ListView):
            permission_required = 'app.view_model'
            # or
            permission_required = ['app.view_model', 'app.change_model']
    """
    permission_required = None
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_permission_required(self):
        """Get the required permissions for this view."""
        if isinstance(self.permission_required, str):
            return [self.permission_required]
        return self.permission_required or []

    def test_func(self):
        """Test if user has required permissions."""
        user = self.request.user
        if not user.is_authenticated:
            return False

        required_perms = self.get_permission_required()
        if not required_perms:
            return True

        return user.has_perms(required_perms)

    def handle_no_permission(self):
        """Handle case when user doesn't have permission."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        # Log permission denial
        logger.warning(
            f"Permission denied for user {self.request.user.username} "
            f"accessing {self.request.path} - Required: {self.get_permission_required()}"
        )

        messages.error(
            self.request,
            "You don't have permission to access this resource."
        )
        return redirect('dashboard:index')


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for class-based views that require specific roles.

    Usage:
        class MyView(RoleRequiredMixin, ListView):
            role_required = 'manager'
            # or
            role_required = ['manager', 'hr_manager']
    """
    role_required = None
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_role_required(self):
        """Get the required roles for this view."""
        if isinstance(self.role_required, str):
            return [self.role_required]
        return self.role_required or []

    def test_func(self):
        """Test if user has required role."""
        user = self.request.user
        if not user.is_authenticated:
            return False

        required_roles = self.get_role_required()
        if not required_roles:
            return True

        return has_role(user, required_roles)

    def handle_no_permission(self):
        """Handle case when user doesn't have required role."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        # Log role denial
        logger.warning(
            f"Role access denied for user {self.request.user.username} "
            f"accessing {self.request.path} - Required: {self.get_role_required()}"
        )

        messages.error(
            self.request,
            "You don't have the required role to access this resource."
        )
        return redirect('dashboard:index')


def require_permission(permission: Union[str, List[str]], login_url='/accounts/login/'):
    """
    Decorator for function-based views that require specific permissions.

    Usage:
        @require_permission('app.view_model')
        def my_view(request):
            ...

        @require_permission(['app.view_model', 'app.change_model'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url=login_url)
        def _wrapped_view(request, *args, **kwargs):
            if isinstance(permission, str):
                perms = [permission]
            else:
                perms = permission

            if not request.user.has_perms(perms):
                # Log permission denial
                logger.warning(
                    f"Permission denied for user {request.user.username} "
                    f"accessing {request.path} - Required: {perms}"
                )

                messages.error(
                    request,
                    "You don't have permission to access this resource."
                )
                return redirect('dashboard:index')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_role(role: Union[str, List[str]], login_url='/accounts/login/'):
    """
    Decorator for function-based views that require specific roles.

    Usage:
        @require_role('manager')
        def my_view(request):
            ...

        @require_role(['manager', 'hr_manager'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url=login_url)
        def _wrapped_view(request, *args, **kwargs):
            if isinstance(role, str):
                roles = [role]
            else:
                roles = role

            if not has_role(request.user, roles):
                # Log role denial
                logger.warning(
                    f"Role access denied for user {request.user.username} "
                    f"accessing {request.path} - Required: {roles}"
                )

                messages.error(
                    request,
                    "You don't have the required role to access this resource."
                )
                return redirect('dashboard:index')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def has_role(user, roles: Union[str, List[str]]) -> bool:
    """
    Check if user has any of the specified roles.

    Args:
        user: Django User instance
        roles: Single role string or list of role strings

    Returns:
        bool: True if user has any of the roles
    """
    if not user or not user.is_authenticated:
        return False

    if isinstance(roles, str):
        roles = [roles]

    # Check superuser first (has all permissions)
    if user.is_superuser:
        return True

    # Check staff status
    if user.is_staff and 'staff' in roles:
        return True

    # Check for role-based groups or custom user attributes
    user_role = get_user_role(user)
    return user_role in roles


def get_user_role(user) -> str:
    """
    Get the primary role of a user based on their permissions and attributes.

    Returns:
        str: User role ('superuser', 'manager', 'hr_manager', etc.)
    """
    if not user or not user.is_authenticated:
        return 'anonymous'

    if user.is_superuser:
        return 'superuser'

    # Check for customer attribute
    if getattr(user, 'is_customer', False):
        return 'customer'

    # Check role-based permissions
    if user.has_perm('human_resources.manage_employee_records'):
        return 'hr_manager'
    elif user.has_perm('inventory.manage_inventory_categories'):
        return 'inventory_manager'
    elif user.has_perm('sales.manage_sales_promotions'):
        return 'sales_person'
    elif user.has_perm('store_management.manage_store_settings'):
        return 'manager'
    elif user.is_staff:
        return 'staff'

    return 'customer'


def get_user_permissions(user) -> List[str]:
    """
    Get all permissions for a user.

    Returns:
        List[str]: List of permission codenames
    """
    if not user or not user.is_authenticated:
        return []

    return list(user.get_all_permissions())


def has_permission_group(user, group_name: str) -> bool:
    """
    Check if user has all permissions in a permission group.

    Args:
        user: Django User instance
        group_name: Name of permission group

    Returns:
        bool: True if user has all permissions in the group
    """
    if group_name not in PERMISSION_GROUPS:
        return False

    required_perms = PERMISSION_GROUPS[group_name]
    return user.has_perms(required_perms)


def get_user_permission_groups(user) -> List[str]:
    """
    Get all permission groups that a user has access to.

    Returns:
        List[str]: List of permission group names
    """
    groups = []
    for group_name in PERMISSION_GROUPS:
        if has_permission_group(user, group_name):
            groups.append(group_name)
    return groups


def can_access_module(user, module_name: str) -> bool:
    """
    Check if user can access a specific module.

    Args:
        user: Django User instance
        module_name: Name of the module

    Returns:
        bool: True if user can access the module
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser can access everything
    if user.is_superuser:
        return True

    # Check if user has any permission in the module's permission group
    if module_name in PERMISSION_GROUPS:
        required_perms = PERMISSION_GROUPS[module_name]
        return any(user.has_perm(perm) for perm in required_perms)

    return False


def get_accessible_modules(user) -> List[str]:
    """
    Get list of modules that a user can access.

    Returns:
        List[str]: List of accessible module names
    """
    modules = []
    for module_name in PERMISSION_GROUPS:
        if can_access_module(user, module_name):
            modules.append(module_name)
    return modules


def log_permission_check(user, permission: str, granted: bool, resource: str = None):
    """
    Log permission check for audit purposes.

    Args:
        user: Django User instance
        permission: Permission being checked
        granted: Whether permission was granted
        resource: Optional resource being accessed
    """
    if not user or not user.is_authenticated:
        return

    status = "GRANTED" if granted else "DENIED"
    resource_info = f" - Resource: {resource}" if resource else ""

    logger.info(
        f"PERMISSION_CHECK {status} - User: {user.username} "
        f"Permission: {permission}{resource_info} - IP: {getattr(user, '_ip_address', 'unknown')}"
    )


def get_role_hierarchy() -> dict:
    """
    Get the role hierarchy definition.

    Returns:
        dict: Role hierarchy with levels
    """
    return ROLE_HIERARCHY.copy()


def get_permission_groups() -> dict:
    """
    Get all permission groups and their permissions.

    Returns:
        dict: Permission groups mapping
    """
    return PERMISSION_GROUPS.copy()


def check_role_hierarchy(user_role: str, required_role: str) -> bool:
    """
    Check if user role meets the required role level in hierarchy.

    Args:
        user_role: User's current role
        required_role: Required role level

    Returns:
        bool: True if user role level >= required role level
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 100)

    return user_level >= required_level


def get_higher_roles(role: str) -> List[str]:
    """
    Get all roles that are higher or equal in hierarchy to the given role.

    Args:
        role: Base role to compare against

    Returns:
        List[str]: List of roles with higher or equal hierarchy
    """
    base_level = ROLE_HIERARCHY.get(role, 0)
    return [r for r, level in ROLE_HIERARCHY.items() if level >= base_level]


def get_lower_roles(role: str) -> List[str]:
    """
    Get all roles that are lower or equal in hierarchy to the given role.

    Args:
        role: Base role to compare against

    Returns:
        List[str]: List of roles with lower or equal hierarchy
    """
    base_level = ROLE_HIERARCHY.get(role, 0)
    return [r for r, level in ROLE_HIERARCHY.items() if level <= base_level]


def validate_permission_structure():
    """
    Validate that the permission structure is consistent and complete.

    Returns:
        dict: Validation results with any issues found
    """
    issues = []

    # Check that all permissions in groups are properly formatted
    for group_name, permissions in PERMISSION_GROUPS.items():
        for perm in permissions:
            if not isinstance(perm, str) or '.' not in perm:
                issues.append(f"Invalid permission format in {group_name}: {perm}")

    # Check role hierarchy for consistency
    if len(ROLE_HIERARCHY) == 0:
        issues.append("Role hierarchy is empty")

    return {
        'valid': len(issues) == 0,
        'issues': issues
    }


# Initialize validation on module load
_validation_result = validate_permission_structure()
if not _validation_result['valid']:
    logger.warning(f"Permission structure validation issues: {_validation_result['issues']}")
