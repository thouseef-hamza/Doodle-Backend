from django.contrib.auth.backends import BaseBackend
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class UserAuthBackend(BaseBackend):
    def authenticate(
        self, request, unique_code=None, email=None, password=None, **kwargs
    ):
        # This User either Institute nor Student
        if unique_code:
            print("auth backends unique code")
            try:
                user = User.objects.get(unique_code=unique_code)

                if user.check_password(password):
                    return user
                raise AuthenticationFailed("Password is not Correct")

            except User.DoesNotExist:
                return None

        # This User is Our Teacher
        if email:
            print("auth backends EMAIL code")
            try:
                user = User.objects.get(email=email)

                if user.check_password(password):
                    return user
                raise AuthenticationFailed("Password is not Correct")

            except User.DoesNotExist:
                return None
