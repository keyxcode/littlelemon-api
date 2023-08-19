from django.urls import path, include
from . import views

urlpatterns = [
    path("", include("djoser.urls")),
    path("auth", include("djoser.urls.authtoken")),
]
