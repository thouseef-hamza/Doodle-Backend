from django.urls import path
from .. import views


urlpatterns = [
    path(
        "profile/",
        views.InstituteProfileGetUpdateAPIView.as_view(),
        name="institute-profile-get-update",
    ),
    path(
        "batches/", views.BatchListCreateAPIView.as_view(), name="batches-create-list"
    ),
    path(
        "batch/<int:pk>/",
        views.BatchGetUpdateAPIView.as_view(),
        name="batch-get-update",
    ),
    path(
        "students/",
        views.StudentListCreateAPIView.as_view(),
        name="students-create-list",
    ),
    path(
        "student/<int:pk>/",
        views.StudentGetUpdateAPIView.as_view(),
        name="student-get-update",
    ),
    path(
        "dashboard/", views.InstituteDashboardAPIView.as_view(), name="dashboard-view"
    ),
    path(
        "payments/detail/",
        views.InstitutePaymentDetailListCreateAPIView.as_view(),
        name="institute-payment-detail-list-create",
    ),
    path(
        "payments/detail/<int:pk>/",
        views.InstitutePaymentDetailRetrieveUpdateAPIView.as_view(),
        name="institute-payment-detail-retrieve-update",
    ),
    path(
        "students/payments/<int:pk>/", views.StudentPaymentListCreateAPIView.as_view()
    ),
]
