from django.db import models
from accounts.models import User

# Create your models here.

class Institute(models.Model):
     user=models.OneToOneField(User,on_delete=models.SET_NULL,null=True,related_name='Institute')
     
     def __str__(self):
        return self.user.institute_name if self.user else "No Institute"