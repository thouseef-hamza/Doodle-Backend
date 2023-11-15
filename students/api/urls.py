from django.urls import path
from .. import views

urlpatterns = [
    path("profile/", views.StudentUpdateAPIView.as_view(), name="student-profile")
]
