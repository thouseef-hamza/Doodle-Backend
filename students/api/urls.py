from django.urls import path
from .. import views

urlpatterns = [
    path("profile/", views.UserStudentUpdateAPIView.as_view(), name="student-profile"),
    # path("tasks"),
    # path("task/<int:pk>/")
]
