from django.db import models
from accounts.models import User

# Create your models here.


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, related_name="teacher_profile"
    )

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
        ]
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self):
        return self.user.first_name if self.user else "No Teacher"
