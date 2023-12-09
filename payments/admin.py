from django.contrib import admin
from .models import StudentPayment,UserPaymentDetail

# Register your models here.

admin.site.register(StudentPayment)
admin.site.register(UserPaymentDetail)
