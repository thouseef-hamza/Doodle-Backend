from django.urls import path
from .. import views

urlpatterns = [
    path(
        "institute/",
        views.InstituteTaskListCreateAPIView.as_view(),
        name="ins-task-list-create",
    ),
    path(
        "institute/task/<int:pk>/",
        views.InstituteTaskUpdateAPIView.as_view(),
        name="ins-task-get-update",
    ),
    path(
        "institute/task/<int:task_id>/assignment/",
        views.StudentTaskAssignmentListAPIView.as_view(),
        name="ins-task-student-assignment-update",
    ),
    path(
        "institute/task/<int:task_id>/assignment/<int:pk>/",
        views.StudentTaskAssignmentGetUpdateAPIView.as_view(),
        name="ins-task-student-assignment-update",
    ),
]
