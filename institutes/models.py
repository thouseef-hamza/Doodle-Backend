from django.db import models
from accounts.models import User

# Create your models here.


class InstituteProfile(models.Model):
    user = models.OneToOneField(
        User, models.SET_NULL, null=True, related_name="institute_profile"
    )
