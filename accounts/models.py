from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
     """
     Three User Institute, Admin, Student
     """ 
     email=models.EmailField(unique=True)
     institute_name = models.CharField(null=True,blank=True,max_length=60)
     phone_number = models.CharField(unique=True,max_length=15)
     is_institute = models.BooleanField(default=False)
     is_student = models.BooleanField(default=False)
     is_teacher = models.BooleanField(default=False)
     is_blocked = models.BooleanField(default=False)
     unique_code = models.CharField(max_length=20,unique=True,blank=True,null=True)
     
     USERNAME_FIELD='email'
     REQUIRED_FIELDS=["phone_number","username"]
     
