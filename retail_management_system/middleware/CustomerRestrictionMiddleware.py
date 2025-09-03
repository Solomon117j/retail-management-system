from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

class CustomerRestrictionMiddleware(MiddlewareMixin):
    """
    Middleware to restrict access to certain views for customers
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Define restricted paths for customers
        self.restricted_paths = [
            '/admin/',
            '/human_resources/',
            '/inventory/',
            '/sales/',
            '/procurement/',
            '/store_management/',
            '/reporting/',
        ]

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # Assuming user model has is_customer attribute
            if getattr(user, 'is_customer', False):
                path = request.path_info
                if any(path.startswith(p) for p in self.restricted_paths):
                    return HttpResponseForbidden("Access denied for customers to this resource.")

        response = self.get_response(request)
        return response
