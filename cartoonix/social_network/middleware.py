from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

EXEMPT_URLS = [reverse('login_page'), reverse('register_user')]  # URLs, которые не требуют аутентификации

class LoginRequiredMiddleware:
    """
    Middleware для перенаправления незалогиненных пользователей на страницу логина
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Если пользователь не залогинен и пытается получить доступ к URL, кроме exempt (например, login)
            if request.path not in EXEMPT_URLS:
                return redirect('login_page')
        
        response = self.get_response(request)
        return response