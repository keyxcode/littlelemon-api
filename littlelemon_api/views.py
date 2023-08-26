from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import generics, status
from rest_framework import viewsets
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from .serializers import (
    UserSerializer,
    MenuItemSerializer,
    CategorySerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
)
from .permissions import IsManager
from .models import MenuItem, Category, Cart, Order, OrderItem


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def managers_list(request):
    if request.method == "GET":
        users = User.objects.filter(groups__name="Manager")
        serialized_users = UserSerializer(users, many=True)

        return Response(serialized_users.data)

    if request.method == "POST":
        username = request.POST.get("username", None)

        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)

            return Response(
                {"message": f"assigned user {user} to group Manager"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"message": "missing username"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def managers_details(request, pk):
    user = get_object_or_404(User, pk=pk)
    managers = Group.objects.get(name="Manager")
    managers.user_set.remove(user)

    return Response({"message": f"removed user {user} from group Manager"})


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser | IsManager])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def delivery_crew_list(request):
    print(request.user)
    if request.method == "GET":
        users = User.objects.filter(groups__name="Delivery Crew")
        serialized_users = UserSerializer(users, many=True)

        return Response(serialized_users.data)

    if request.method == "POST":
        username = request.POST.get("username", None)

        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name="Delivery Crew")
            delivery_crew.user_set.add(user)

            return Response(
                {"message": f"assigned user {user} to group Delivery Crew"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"message": "missing username"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["DELETE"])
@permission_classes([IsAdminUser | IsManager])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def delivery_crew_details(request, pk):
    user = get_object_or_404(User, pk=pk)
    delivery_crew = Group.objects.get(name="Delivery Crew")
    delivery_crew.user_set.remove(user)

    return Response({"message": f"removed user {user} from group Delivery Crew"})


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        return super(CategoryList, self).get_permissions()


class MenuItemsViewsSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    ordering_fields = ["price"]
    filterset_fields = ["title", "category"]

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            permission_classes = []
        elif self.action == "create":
            permission_classes = [IsAdminUser | IsManager]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def cart_list(request):
    if request.method == "GET":
        cart_items = Cart.objects.filter(user=request.user)
        serialized_cart_items = CartSerializer(cart_items, many=True)

        return Response(serialized_cart_items.data)

    if request.method == "POST":
        serialized_item = CartSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)

        menu_item = serialized_item.validated_data["menuitem"]
        quantity = serialized_item.validated_data["quantity"]
        unit_price = menu_item.price
        price = unit_price * int(quantity)

        try:
            created_item = serialized_item.save(
                user=request.user,
                unit_price=unit_price,
                price=price,
            )
        except Exception as e:
            return Response({"message": str(e)})

        return Response(CartSerializer(created_item).data)

    if request.method == "DELETE":
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def order_list(request):
    if request.method == "GET":
        if (
            request.user.groups.filter(name="Manager").exists()
            or request.user.is_superuser
        ):
            orders = Order.objects.all()
        elif request.user.groups.filter(name="Delivery Crew").exists():
            orders = Order.objects.filter(delivery_crew=request.user)
        else:
            orders = Order.objects.filter(user=request.user)

        serialized_orders = OrderSerializer(orders, many=True)
        return Response(serialized_orders.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        cart = Cart.objects.filter(user=request.user)

        if len(cart) == 0:
            return Response(
                {"message": "cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        total = sum(cart_item.price for cart_item in cart)
        order = Order.objects.create(user=request.user, status=False, total=total)
        serialized_order = OrderSerializer(order)

        for cart_item in cart:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price,
            )

        cart.delete()

        return Response(serialized_order.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def order_details(request, pk):
    order = Order.objects.get(pk=pk)

    if request.method == "GET":
        if (
            request.user != order.user
            and not request.user.groups.filter(
                name__in=["Delivery Crew", "Manager"]
            ).exists()
            and not request.user.is_superuser
        ):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        order_items = OrderItem.objects.filter(order=order)
        serialized_order_items = OrderItemSerializer(order_items, many=True)

        return Response(serialized_order_items.data, status=status.HTTP_200_OK)

    if request.method == "PUT" or request.method == "PATCH":
        if (
            not request.user.groups.filter(
                name__in=["Delivery Crew", "Manager"]
            ).exists()
            and not request.user.is_superuser
        ):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if request.user.groups.filter(name="Delivery Crew").exists() and (
            "status" not in request.data or len(request.data) > 1
        ):
            return Response(
                {"message": "Delivery crew can only change the order status"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serialized_order = OrderSerializer(order, data=request.data, partial=True)
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save()

        return Response(serialized_order.data)

    if request.method == "DELETE":
        if not request.user.groups.filter(name="Manager").exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
