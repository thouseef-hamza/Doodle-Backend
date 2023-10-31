from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class User(AbstractUser):
    # Three User Institute, Teacher, Student
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, blank=True, null=True, unique=True)
    phone_number = models.CharField(unique=True, max_length=15, blank=True, null=True)
    is_institute = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    unique_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    verification_sid = models.CharField(max_length=55, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "username"]

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return super().get_full_name()
