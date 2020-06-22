from django.contrib import auth
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin


class IapUserLoginMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not (request.user and request.user.is_authenticated):
            user = auth.authenticate(request)
            if user is None:
                return HttpResponseForbidden()
            request.user = user
            auth.login(request, user)
