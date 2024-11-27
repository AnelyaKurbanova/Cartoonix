import logging
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger('middleware_logger')

EXEMPT_URLS = [reverse('login_page'), reverse('register_user')]


class LoginRequiredMiddleware:
    """
    Middleware for redirecting unauthorized users to the login page
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if request.path not in EXEMPT_URLS:
                logger.warning(f"Unauthenticated access attempt to {request.path}. Redirecting to login page.")
                return redirect('login_page')

        response = self.get_response(request)
        return response
