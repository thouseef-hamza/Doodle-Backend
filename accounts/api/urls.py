from django.urls import path
from .. import views


urlpatterns = [
    path(
        "institute/register/",
        views.InstituteRegisterationAPIView.as_view(),
        name="institute-register",
    ),
    path("user/login/", views.UserLoginAPIVew.as_view(), name="user-login"),
    path("user/verify-otp/", views.OTPVerificationAPIView.as_view(), name="user-verify-otp"),
    path("user/change-password/",views.ChangePasswordAPIView.as_view(),name='user-change-password'),
]
