from django.db import models
from accounts.models import User
from django.contrib.auth import get_user_model
# Create your models here.


class InstituteProfile(models.Model):
    user = models.OneToOneField(
        User, models.CASCADE,related_name='profile',primary_key=True
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    establishment_year = models.PositiveIntegerField(blank=True,null=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
        ]
        verbose_name = "Institute Profile"
        verbose_name_plural = "Institute Profiles"


class Batch(models.Model):
    user = models.ForeignKey(InstituteProfile, models.SET_NULL, null=True,default='Batch')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"

    def __str__(self) -> str:
        return self.name
