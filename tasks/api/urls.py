from django.urls import path
from .. import views

urlpatterns = [
    path(
        "institute/",
        views.InstituteTaskListCreateAPIView.as_view(),
        name="ins-task-list-create",
    ),
    path(
        "institute/<int:pk>/",
        views.InstituteTaskUpdateAPIView.as_view(),
        name="ins-task-get-update",
    ),
    path(
        "institute/<int:task_id>/task/<int:pk>/",
        views.StudentTaskAssignmentGetUpdateAPIView.as_view(),
        name="ins-task-student-assignment-update",
    ),
]
