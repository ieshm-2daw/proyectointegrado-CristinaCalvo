from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.baneado:
            if request.path != reverse('error'):
                return redirect(reverse('error'))
        return self.get_response(request)
