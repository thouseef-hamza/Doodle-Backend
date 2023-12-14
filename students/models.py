from django.db import models
from accounts.models import User
from datetime import date
from django.conf import settings

# Create your models here.

GENDER_CHOICES = [
    ("S", "Select"),
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )
    batch = models.ForeignKey(
        "institutes.Batch",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="student_batch",
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="S")
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.URLField(
        default=settings.CLOUDINARY_DEFAULT_STUDENT_IMAGE_LINK
    )
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return self.user.first_name if self.user else "No Student"


