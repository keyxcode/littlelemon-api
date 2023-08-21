from django.urls import path, include
from . import views

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("groups/manager/users", views.managers_list),
    path("groups/manager/users/<int:pk>", views.managers_details),
    path("groups/delivery-crew/users", views.delivery_crew_list),
    path("groups/delivery-crew/users/<int:pk>", views.delivery_crew_details),
    path("menu-items", views.MenuItemsList.as_view()),
    path("categories", views.CategoryList.as_view()),
]
