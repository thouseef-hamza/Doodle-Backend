from django.urls import path
from .. import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path(
        "institute/register/",
        views.InstituteRegisterationAPIView.as_view(),
        name="institute-register",
    ),
    path(
        "teacher/register/",
        views.TeacherRegisterationAPIView.as_view(),
        name="teacher-register",
    ),
    path("user/login/", views.UserLoginAPIVew.as_view(), name="user-login"),
    path(
        "user/verify-otp/<int:pk>/",
        views.OTPVerificationAPIView.as_view(),
        name="user-verify-otp",
    ),
    path(
        "user/change-password/",
        views.ChangePasswordAPIView.as_view(),
        name="user-change-password",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
