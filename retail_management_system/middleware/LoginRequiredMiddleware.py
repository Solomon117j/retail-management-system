from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires login for all views except those explicitly exempted
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't require authentication
        self.exempt_urls = [
            '/accounts/login/',
            '/accounts/login/generic/',
            '/accounts/login/customer/',
            '/accounts/login/staff/',
            '/accounts/register/',
            '/accounts/logout/',
            '/accounts/password_reset/',
            '/accounts/password_reset/done/',
            '/accounts/reset/',
            '/accounts/reset/done/',
            '/accounts/confirm/',
            '/accounts/confirm/done/',
            '/admin/login/',
            '/api/health/',
            '/api/docs/',
            '/static/',
            '/media/',
        ]

        # Add debug toolbar URLs if in debug mode
        if settings.DEBUG:
            self.exempt_urls.extend([
                '/__debug__/',
            ])

    def __call__(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Check if the current path is exempt
            path = request.path_info
            if not any(path.startswith(url) for url in self.exempt_urls):
                # Redirect to login page
                try:
                    login_url = reverse('accounts:login')
                except NoReverseMatch:
                    login_url = settings.LOGIN_URL
                return redirect(f'{login_url}?next={request.path}')

        response = self.get_response(request)
        return response
