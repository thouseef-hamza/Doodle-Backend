from django.urls import path
from .. import views

urlpatterns = [
    path(
        "profile/",
        views.UserStudentRetrieveUpdateAPIView.as_view(),
        name="student-profile",
    ),
    path("classmates/", views.ClassmatesListAPIView.as_view()),
    path("task/", views.UserStudentTaskListAPIView.as_view()),
    path("task/<int:pk>/", views.UserStudentTaskRetrieveUpdateAPIView.as_view()),
    path("stripe/create/checkout/session/",views.StripeCheckoutAPIView.as_view(),name="create-checkout-session")
]
