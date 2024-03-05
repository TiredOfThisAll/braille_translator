from django.urls import include, path

urlpatterns = [
    path("", include("braille_web.urls")),
]