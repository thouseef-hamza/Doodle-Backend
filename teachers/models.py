from django.db import models
from accounts.models import User

# Create your models here.

class Teacher(models.Model):
     user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,related_name='Teacher')
     
     def __str__(self):
        return self.user.first_name if self.user else "No Teacher"