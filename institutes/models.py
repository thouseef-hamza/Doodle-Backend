from django.db import models
from accounts.models import User
from teachers.models import TeacherProfile
from datetime import datetime
from django.utils import timezone
from payments.models import UserPaymentDetail
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
    start_date = models.DateTimeField(null=True)
    description = models.TextField(blank=True, null=True)
    institute_payment_detail = models.ForeignKey(
        UserPaymentDetail, on_delete=models.CASCADE, null=True
    )
    batch_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fee_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    scheduled_date = models.DateTimeField(null=True)
    is_scheduled = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True)

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
    salary = models.PositiveIntegerField(default=35_000)

    def __str__(self) -> str:
        return self.title


class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEW = "review", "Review"
        REJECTED = "rejected", "Rejected"
        ACCEPTED = "accepted", "Accepted"

    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="job_application"
    )
    applicant = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="job_applicant"
    )
    application_date = models.DateTimeField(auto_now_add=True)
    resume = models.URLField()
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )

    def __str__(self) -> str:
        return self.applicant
