# retail_management_system/middleware.py
from django.shortcuts import redirect
from django.conf import settings

import logging

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('middleware.LoginRequired')

    def __call__(self, request):
        # Define landing page path
        landing_page = '/'
        
        # Paths that unauthenticated users are allowed to access
        exact_open_urls = [
            landing_page,
            '/favicon.ico',
            '/static/',
            '/media/',
        ]
        prefix_open_urls = ['/static/', '/media/']

        self.logger.debug(f"LoginRequiredMiddleware: request.path={request.path}, user_authenticated={request.user.is_authenticated}")

        # If user is authenticated, allow request
        if request.user.is_authenticated:
            return self.get_response(request)

        # If unauthenticated and accessing landing page, allow
        if request.path == landing_page or any(request.path.startswith(url) for url in prefix_open_urls):
            return self.get_response(request)

        # Redirect all other unauthenticated requests to landing page
        if request.path != landing_page:
            self.logger.debug(f"Redirecting unauthenticated user to landing page: {landing_page}")
            return redirect(f'{landing_page}?next={request.path}')

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
