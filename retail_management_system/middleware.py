# retail_management_system/middleware.py
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # URLs that don't require authentication
        open_urls = [
            '/accounts/login/',
            '/admin/login/',
            '/admin/',
            '/favicon.ico',
            '/static/',
        ]
        
        # Check if path requires authentication
        if not request.user.is_authenticated and not any(
            request.path.startswith(url) for url in open_urls
        ):
            # Avoid redirect loops by checking if we're already going to login
            if request.path != settings.LOGIN_URL:
                return redirect(settings.LOGIN_URL + f'?next={request.path}')
        
        return self.get_response(request)