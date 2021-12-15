from django.shortcuts import redirect
from django.contrib.auth.models import User

def auth_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        if not request.user.is_authenticated:
            return redirect('/')
        response = get_response(request)
        return response

    return middleware