# Created by elham at 11/29/20

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason


class SafeJWTAuthentication(BaseAuthentication):
    """
        custom authentication class for DRF and JWT
    """

    def authenticate(self, request):

        User = get_user_model()
        authorization_heaader = request.headers.get('Authorization')

        if not authorization_heaader:
            return None
        try:
            # header = 'Token xxxxxxxxxxxxxxxxxxxxxxxx'
            access_token = authorization_heaader.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')

        user = User.objects.filter(id=payload['user_id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        if request.method == 'GET' and not payload.get('get_post'):
            raise exceptions.PermissionDenied('Access Denied')

        if request.method == 'POST' and not payload.get('create_post'):
            raise exceptions.PermissionDenied('Access Denied')

        if (request.method == 'PUT' or request.method == 'PATCH') and not payload.get('edit_post'):
            raise exceptions.PermissionDenied('Access Denied')

        if request.method == 'DELETE' and not payload.get('delete_post'):
            raise exceptions.PermissionDenied('Access Denied')

        return user, None
