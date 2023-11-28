from django.db import models
from accounts.models import User
from teachers.models import TeacherProfile

# Create your models here.


class InstituteProfile(models.Model):
    user = models.OneToOneField(
        User, models.CASCADE, related_name="institute_profile", primary_key=True
    )
    profile_image = models.ImageField(upload_to="profile/", null=True, blank=True)
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


class AbstractDate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Job(AbstractDate):
    class JobCategory(models.TextChoices):
        FULL_TIME = "full-time", "Full-Time"
        PART_TIME = "part-time", "Part-Time"

    class JobType(models.TextChoices):
        REMOTE = "remote", "Remote"
        ONSITE = "onsite", "Onsite"

    title = models.CharField(max_length=100)
    requirements = models.TextField(default="", blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=JobCategory.choices, default=JobCategory.FULL_TIME
    )
    job_type = models.CharField(
        max_length=20, choices=JobType.choices, default=JobType.REMOTE
    )
    company = models.ForeignKey(
        InstituteProfile, on_delete=models.CASCADE, related_name="institute_jobs"
    )
    salary=models.PositiveIntegerField(default=35_000)

    def __str__(self) -> str:
        return self.title


class Application(models.Model):
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="job_application"
    )
    applicant = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="job_applicant"
    )
    application_date=models.DateTimeField(auto_now_add=True)
    resume=models.URLField()
    
    def __str__(self) -> str:
        return self.applicant
    
