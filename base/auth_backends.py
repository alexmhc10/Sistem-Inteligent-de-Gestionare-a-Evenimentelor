from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from base.models import PersonalLocation

class PersonalLocationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = PersonalLocation.objects.get(username=username)
            if check_password(password, user.password):
                return user
        except PersonalLocation.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return PersonalLocation.objects.get(pk=user_id)
        except PersonalLocation.DoesNotExist:
            return None
