from django.db import models
from accounts.models import User
from django.conf import settings

# Create your models here.


class InstituteProfile(models.Model):
    user = models.OneToOneField(
        User, models.CASCADE, related_name="institute_profile", primary_key=True
    )
    profile_picture = models.URLField(
        default=settings.CLOUDINARY_DEFAULT_INSTITUTE_IMAGE_LINK
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    establishment_year = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Institute Profile"
        verbose_name_plural = "Institute Profiles"

    def __str__(self) -> str:
        return self.user.get_full_name() if self.user else "No Institute"


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Batch(models.Model):
    institute = models.ForeignKey(InstituteProfile, models.CASCADE, null=True)
    topics = models.ManyToManyField(Topic)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"

    def __str__(self) -> str:
        return self.name
