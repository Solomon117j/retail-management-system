"""
Permission utilities for the retail management system.
This module provides decorators and helper functions for checking permissions.
"""

from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def has_permission(user, permission_codename):
    """
    Check if a user has a specific permission.
    
    Args:
        user: The user object (Employee instance)
        permission_codename: The codename of the permission to check
    
    Returns:
        bool: True if user has the permission, False otherwise
    """
    if user.is_superuser:
        return True
    
    return user.has_perm(f'human_resources.{permission_codename}')


def require_permission(permission_codename, redirect_url=None, message=None):
    """
    Decorator to require a specific permission for a view.
    
    Args:
        permission_codename: The codename of the required permission
        redirect_url: URL to redirect to if permission is denied (optional)
        message: Message to display if permission is denied (optional)
    
    Usage:
        @require_permission('view_inventory')
        def inventory_list(request):
            # View code here
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if not has_permission(request.user, permission_codename):
                if message:
                    messages.error(request, message)
                
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    raise PermissionDenied(
                        f"You don't have permission to access this resource. "
                        f"Required permission: {permission_codename}"
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permission_codenames, redirect_url=None, message=None):
    """
    Decorator to require any one of multiple permissions for a view.
    
    Args:
        permission_codenames: Multiple permission codenames (user needs at least one)
        redirect_url: URL to redirect to if permission is denied (optional)
        message: Message to display if permission is denied (optional)
    
    Usage:
        @require_any_permission('view_inventory', 'edit_inventory')
        def inventory_detail(request, pk):
            # View code here
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            has_any_permission = any(
                has_permission(request.user, perm)
                for perm in permission_codenames
            )
            
            if not has_any_permission:
                if message:
                    messages.error(request, message)
                
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    raise PermissionDenied(
                        f"You don't have permission to access this resource. "
                        f"Required permissions (any): {', '.join(permission_codenames)}"
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(*permission_codenames, redirect_url=None, message=None):
    """
    Decorator to require all specified permissions for a view.
    
    Args:
        permission_codenames: Multiple permission codenames (user needs all)
        redirect_url: URL to redirect to if permission is denied (optional)
        message: Message to display if permission is denied (optional)
    
    Usage:
        @require_all_permissions('view_inventory', 'edit_inventory')
        def inventory_edit(request, pk):
            # View code here
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            missing_permissions = [
                perm for perm in permission_codenames
                if not has_permission(request.user, perm)
            ]
            
            if missing_permissions:
                if message:
                    messages.error(request, message)
                
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    raise PermissionDenied(
                        f"You don't have permission to access this resource. "
                        f"Missing permissions: {', '.join(missing_permissions)}"
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions(user):
    """
    Get all permissions for a user.
    
    Args:
        user: The user object (Employee instance)
    
    Returns:
        list: List of permission codenames the user has
    """
    if user.is_superuser:
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from human_resources.models import Employee
        
        content_type = ContentType.objects.get_for_model(Employee)
        return list(
            Permission.objects.filter(content_type=content_type)
            .values_list('codename', flat=True)
        )
    
    # Get permissions from groups and individual permissions
    permissions = set()
    
    # Add group permissions
    for group in user.groups.all():
        permissions.update(
            group.permissions.filter(content_type__app_label='human_resources')
            .values_list('codename', flat=True)
        )
    
    # Add individual permissions
    permissions.update(
        user.user_permissions.filter(content_type__app_label='human_resources')
        .values_list('codename', flat=True)
    )
    
    return list(permissions)


def get_user_role_groups(user):
    """
    Get all role groups for a user.
    
    Args:
        user: The user object (Employee instance)
    
    Returns:
        list: List of role group names the user belongs to
    """
    return list(
        user.groups.filter(name__startswith='Role: ')
        .values_list('name', flat=True)
    )


class PermissionMixin:
    """
    Mixin for class-based views to check permissions.
    
    Usage:
        class InventoryListView(PermissionMixin, ListView):
            required_permission = 'view_inventory'
            # or
            required_permissions = ['view_inventory', 'access_inventory']
            permission_required_all = True  # Default is False (any permission)
    """
    required_permission = None
    required_permissions = None
    permission_required_all = False
    permission_denied_message = None
    permission_denied_url = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        # Check single permission
        if self.required_permission:
            if not has_permission(request.user, self.required_permission):
                return self.handle_permission_denied()
        
        # Check multiple permissions
        if self.required_permissions:
            if self.permission_required_all:
                # All permissions required
                missing_permissions = [
                    perm for perm in self.required_permissions
                    if not has_permission(request.user, perm)
                ]
                if missing_permissions:
                    return self.handle_permission_denied()
            else:
                # Any permission required
                has_any = any(
                    has_permission(request.user, perm)
                    for perm in self.required_permissions
                )
                if not has_any:
                    return self.handle_permission_denied()
        
        return super().dispatch(request, *args, **kwargs)
    
    def handle_permission_denied(self):
        """Handle permission denied cases"""
        if self.permission_denied_message:
            messages.error(self.request, self.permission_denied_message)
        
        if self.permission_denied_url:
            return redirect(self.permission_denied_url)
        else:
            raise PermissionDenied("You don't have permission to access this resource.")