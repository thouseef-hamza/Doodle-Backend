from django.urls import path
from .. import views


urlpatterns = [
    path("institute/register/",views.InstituteRegisterationAPIView.as_view(),name='institute-register'),
    path("verify-otp/",views.OTPVerificationAPIView.as_view(),name='institute-verify'),
]
