# retail_management_system/middleware.py
from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # URLs that don't require authentication
        open_urls = [
            '/accounts/login/',
            '/accounts/register/',
            '/admin/login/',
            '/admin/',
            '/favicon.ico',
            '/static/',
            '/media/',
        ]
        
        # Check if path requires authentication
        if not request.user.is_authenticated and not any(
            request.path.startswith(url) for url in open_urls
        ):
            # Avoid redirect loops by checking if we're already going to login
            if request.path != settings.LOGIN_URL:
                return redirect(settings.LOGIN_URL + f'?next={request.path}')
        
        return self.get_response(request)

class CustomerRestrictionMiddleware:
    """
    Restrict customers to customer-facing areas only.
    - Allows: e_commerce pages, auth pages, static/media, favicon
    - Redirects '/' to the customer account home for customers
    - Blocks access to admin/HR/inventory/sales/etc. for customers
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        path = request.path

        if user and user.is_authenticated and getattr(user, 'is_customer', False) and not user.is_staff:
            allowed_prefixes = (
                '/e_commerce/',
                '/accounts/login/',
                '/accounts/logout/',
                '/accounts/register/',
                '/static/',
                '/media/',
                '/favicon.ico',
            )

            # If customer hits root, send them to their customer home
            if path == '/':
                return redirect('/e_commerce/customer-accounts/')

            # Allow only whitelisted prefixes
            if not path.startswith(allowed_prefixes):
                return redirect('/e_commerce/customer-accounts/')

        return self.get_response(request)