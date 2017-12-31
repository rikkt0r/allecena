# coding: utf-8

from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import ParseError, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import exception_handler

from ac_common.loggers import api_logger


def allecena_exception_handler(exc, context):
    api_logger.exception(exc)

    response = exception_handler(exc, context)
    if response is not None:
        return response

    return exception_handler(ParseError('Non-default error'), context)


class IsAuthenticatedAndOwnerPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # no user == no need for permissions per user
        if not hasattr(obj, 'user'):
            return True
        return obj.user == request.user


class AllecenaTokenAuth(BasicAuthentication):
    def authenticate(self, request):
        token = request.META.get(_('HTTP_X_AUTH_TOKEN'), None)  # X-Auth-Token
        if not token:
            raise AuthenticationFailed('Auth token not provided')

        user = authenticate(token=token)
        if not user:
            raise AuthenticationFailed(_('Invalid token header'))

        return (user, None)
