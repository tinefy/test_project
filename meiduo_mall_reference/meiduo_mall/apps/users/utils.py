import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

# from .models import User

User = get_user_model()


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        user = self.get_user_by_account(username)
        if user and user.check_password(password):
            return user

    @staticmethod
    def get_user_by_account(account):
        regex = r'^1[3-9]\d{9}$'
        if re.match(regex, account):
            mobile = account
            try:
                user = User.objects.get(mobile=mobile)
            except User.DoesNotExist:
                return None
            else:
                return user
        else:
            username = account
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
            else:
                return user
