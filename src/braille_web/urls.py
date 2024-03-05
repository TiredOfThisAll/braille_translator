from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "braille_web"
urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("upload/", views.upload_file, name="upload_file"),
    path("upload-status/", views.upload_file_status, name="upload_file_status"),
    path("download/", views.download_file, name="download_file")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
