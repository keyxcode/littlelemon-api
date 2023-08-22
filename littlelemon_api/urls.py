from django.urls import path, include
from . import views

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("groups/manager/users", views.managers_list),
    path("groups/manager/users/<int:pk>", views.managers_details),
    path("groups/delivery-crew/users", views.delivery_crew_list),
    path("groups/delivery-crew/users/<int:pk>", views.delivery_crew_details),
    path("categories", views.CategoryList.as_view()),
    path(
        "menu-items", views.MenuItemsViewsSet.as_view({"get": "list", "post": "create"})
    ),
    path(
        "menu-items/<int:pk>",
        views.MenuItemsViewsSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
]
