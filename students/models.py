from django.db import models
from accounts.models import User

# Create your models here.


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, related_name="Student"
    )
    class Meta:
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return self.user.first_name if self.user else "No Student"
