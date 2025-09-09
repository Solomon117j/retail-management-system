# retail_management_system/middleware.py
from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require authentication - allow exact matches and prefixes
        exact_open_urls = ['/', '/products/', '/accounts/login/', '/accounts/register/', '/admin/login/', '/admin/', '/favicon.ico']
        prefix_open_urls = ['/static/', '/media/']

        # Allow access if user is authenticated or path is in open URLs
        if request.user.is_authenticated:
            return self.get_response(request)

        # For anonymous users, check if path is allowed
        if request.path in exact_open_urls or any(request.path.startswith(url) for url in prefix_open_urls):
            return self.get_response(request)

        # If not allowed, redirect to login (avoid redirect loops)
        if request.path != settings.LOGIN_URL:
            return redirect(settings.LOGIN_URL + f'?next={request.path}')

        return self.get_response(request)

class CustomerRestrictionMiddleware:
    """
    Restrict customers to customer-facing areas only.
    - Allows: e_commerce pages, auth pages, static/media, favicon
    - Redirects '/' to the customer account home for customers
    - Blocks access to admin/HR/inventory/sales/etc. for customers
    - Allows anonymous access to e_commerce pages
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        path = request.path

        # Allow anonymous access to e_commerce pages
        if not user or not user.is_authenticated:
            if path.startswith('/e_commerce/') or path in ['/', '/static/', '/media/', '/favicon.ico']:
                return self.get_response(request)

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

            # If customer hits root, allow landing page instead of redirecting
            if path == '/':
                # Allow landing page for all users, do not redirect
                pass

            # Allow only whitelisted prefixes
            if not path.startswith(allowed_prefixes):
                return redirect('/e_commerce/customer-accounts/')

        return self.get_response(request)
