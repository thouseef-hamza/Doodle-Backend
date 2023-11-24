from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# from rest_framework_swagger.views import get_swagger_view
# schema_view = get_swagger_view(title='Doodle API Documentation')

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("hi", include('rest_framework_swagger.urls')),
    path("api/accounts/", include("accounts.api.urls")),
    path("api/institutes/", include("institutes.api.urls")),
    path("api/students/", include("students.api.urls")),
    path("api/tasks/", include("tasks.api.urls")),
]

# MEDIA Configuration
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
