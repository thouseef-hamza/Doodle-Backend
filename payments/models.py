from django.db import models
from accounts.models import User
from students.models import StudentProfile


class AbstractDate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Create your models here.


class UserPaymentDetail(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_payment_details"
    )
    payment_number = models.CharField(max_length=15)
    payment_qr = models.FileField(upload_to="payments/paymentdetails/",null=True,blank=True)
    payment_bank = models.CharField(max_length=100)
    upi_id = models.CharField(max_length=50)
    
    def __str__(self) -> str:
        return "{} Payment Detail".format(self.user.first_name + " " + self.user.last_name)


class StudentPayment(AbstractDate):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        OVER_DUE = "overdue", "Over Due"

    class PaymentMethod(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        RAZORPAY = "razorpay", "Razorpay"
        PAYPAL = "paypal", "Paypal"

    # User <--- O to O ---> Student Profile ----- O to M ----= Student Payment
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="student_payment_fees"
    )
    sender = models.ForeignKey(UserPaymentDetail, on_delete=models.CASCADE)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_paid = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    fee_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    payment_id = models.CharField(max_length=100, null=True)
    payment_method = models.CharField(
        max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.STRIPE
    )
    is_notified = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return "Payment From {} to {}".format(self.sender.user.first_name + " "+ self.sender.user.last_name,self.student.user.first_name + " " + self.student.user.last_name)
