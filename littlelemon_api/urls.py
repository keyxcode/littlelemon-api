from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter(trailing_slash=False)
router.register("menu-items", views.MenuItemsViewsSet, basename="menu-items")

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
    path("groups/manager/users", views.managers_list),
    path("groups/manager/users/<int:pk>", views.managers_details),
    path("groups/delivery-crew/users", views.delivery_crew_list),
    path("groups/delivery-crew/users/<int:pk>", views.delivery_crew_details),
    path("categories", views.CategoryList.as_view()),
    path("cart/menu-items", views.CartList.as_view()),
]
