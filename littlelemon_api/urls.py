from django.urls import path, include
from . import views

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("groups/manager/users", views.managers),
    path("groups/manager/users/<int:pk>", views.manager),
]
