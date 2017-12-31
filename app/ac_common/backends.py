# coding: utf-8

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils import timezone


class AllecenaAuthenticationBackend(ModelBackend):

    def authenticate(self, email=None, password=None, token=None, **kwargs):        
        if email:
            email = email.lower()
            
        user_cls = get_user_model()

        try:
            if token is not None:
                user = user_cls.objects.get(auth_token=token, auth_expiry_date__gt=timezone.now())
                return user
            else:
                user = user_cls.objects.get(email=email)
                
                if user.is_active and user.check_password(password):
                    return user
                
        except user_cls.DoesNotExist:
            return None

        return None

    def get_user(self, user_id):

        user_cls = get_user_model()
        try:
            return user_cls.objects.get(pk=user_id)
        except user_cls.DoesNotExist:
            return None


class FacebookAuthenticationBackend(ModelBackend):

    def authenticate(self, email=None, password=None, **kwargs):        
        import requests
        r = requests.get("https://graph.facebook.com/me", params={'access_token': password})
                
        if not r.status_code == 200 or 'error' in r.json().keys():
            return None
        
        user_cls = get_user_model()
        user = None

        try:
            user = user_cls.objects.get(email=email.lower())
        except user_cls.DoesNotExist:
            pass
        
        if not user:
            from ac_common.models import User
            user = User.objects.create(email=email.lower(), auth_type=User.AUTH_FACEBOOK, password="facebook")

        return user
