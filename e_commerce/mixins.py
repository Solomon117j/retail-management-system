from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import CustomerAccount

class CustomerAccessMixin(UserPassesTestMixin):
    """
    Mixin to ensure that a user can only access their own customer account.
    """
    def test_func(self):
        # Check if the user is authenticated
        if not self.request.user.is_authenticated:
            return False
        
        # Get the customer account associated with the user
        try:
            customer_account = CustomerAccount.objects.get(user=self.request.user)
        except CustomerAccount.DoesNotExist:
            return False
        
        # Allow access if the account matches the logged-in user
        return self.get_object() == customer_account

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to access this account.")
