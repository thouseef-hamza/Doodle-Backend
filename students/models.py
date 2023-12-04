from django.db import models
from accounts.models import User
from institutes.models import Batch
from datetime import date
from django.conf import settings
from institutes.models import InstituteProfile

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
        Batch,
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


class StudentPayment(models.Model):
    class PaymentMethod(models.TextChoices):
        RAZORPAY = "razorpay", "RazorPay"
        PAYPAL = "paypal", "Paypal"

    class PaymentStatus(models.TextChoices):
        PAID = "paid", "Paid"
        LATE = "late", "Late"
        NOT_PAID = "not_paid", "Not Paid"

    created_by = models.ForeignKey(
        InstituteProfile, on_delete=models.SET_NULL, null=True
    )
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="student_payments"
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.RAZORPAY
    )
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.NOT_PAID
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
