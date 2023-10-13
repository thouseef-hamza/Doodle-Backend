from django.urls import path
from .. import views



urlpatterns = [
    path('profile/',views.InstituteProfileAPIView.as_view(),name='institute-profile'),
    path('profile/update/',views.InstituteProfileUpdateAPIView.as_view(),name='institute-profile-update'),
]
