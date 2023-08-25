from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register("menu-items", views.MenuItemsViewsSet, basename="menu-items")

urlpatterns = [
    path("", include(router.urls)),
    path("groups/manager/users", views.managers_list),
    path("groups/manager/users/<int:pk>", views.managers_details),
    path("groups/delivery-crew/users", views.delivery_crew_list),
    path("groups/delivery-crew/users/<int:pk>", views.delivery_crew_details),
    path("categories", views.CategoryList.as_view()),
    path("cart/menu-items", views.cart_list),
    path("orders", views.order_list),
    path("orders/<int:pk>", views.order_details),
]
