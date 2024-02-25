from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from .models import Owner

class OwnerAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username = None, password = None):
        try:
            owner = Owner.objects.get(email = username)
            if owner.check_password(password):
                return owner
        except Owner.DoesNotExist:
            pass

    def get_user(self, user_id):
        try:
            return Owner.objects.get(pk = user_id)
        except Owner.DoesNotExist:
            return None