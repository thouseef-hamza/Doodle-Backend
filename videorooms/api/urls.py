from django.urls import path
from .. import views

urlpatterns = [
    path("", views.ClassRoomListCreateAPIView.as_view(), name="classroom-list-create"),
    path(
        "<int:pk>/",
        views.ClassRoomRetrieveUpdateAPIView.as_view(),
        name="classroom-update",
    ),
]
