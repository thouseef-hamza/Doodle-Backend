from django.db import models
from accounts.models import User

# Create your models here.


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="teacher_profile"
    )
    profile_picture = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self):
        return self.user.first_name if self.user else "No Teacher"


class Education(models.Model):
    class EducationType(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        ONLINE = "online", "Online"
        COURSE = "course", "Course"
        SELF = "self", "Self"

    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="teacher_education"
    )
    name = models.CharField(max_length=50)
    education_type = models.CharField(
        max_length=10, choices=EducationType.choices, default=EducationType.SELF
    )
    location = models.CharField(max_length=100, null=True, blank=True)


class Experience(models.Model):
    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="teacher_experience"
    )
    job_title = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
