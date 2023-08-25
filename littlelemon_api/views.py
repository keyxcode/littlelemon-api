from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import generics, status
from rest_framework import viewsets
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
from .permissions import IsManager, IsDeliveryCrew
from .models import MenuItem, Category, Cart, Order, OrderItem


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def managers_list(request):
    if request.method == "GET":
        users = User.objects.filter(groups__name="Manager")
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)

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

    return Response({"message": "unknown error"})


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def managers_details(request, pk):
    user = get_object_or_404(User, pk=pk)
    managers = Group.objects.get(name="Manager")
    managers.user_set.remove(user)

    return Response({"message": f"removed user {user} from group Manager"})


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser | IsManager])
def delivery_crew_list(request):
    print(request.user)
    if request.method == "GET":
        users = User.objects.filter(groups__name="Delivery Crew")
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)

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

    return Response({"message": "unknown error"})


@api_view(["DELETE"])
@permission_classes([IsAdminUser | IsManager])
def delivery_crew_details(request, pk):
    user = get_object_or_404(User, pk=pk)
    delivery_crew = Group.objects.get(name="Delivery Crew")
    delivery_crew.user_set.remove(user)

    return Response({"message": f"removed user {user} from group Delivery Crew"})


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == "POST" and self.request.data:
            self.permission_classes = [IsAdminUser]
        return super(CategoryList, self).get_permissions()


class MenuItemsViewsSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
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
def cart_list(request):
    if request.method == "GET":
        cart_items = Cart.objects.filter(user=request.user)
        serialized_cart_items = CartSerializer(cart_items, many=True)

        return Response(serialized_cart_items.data)

    if request.method == "POST":
        serialized_item = CartSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)

        item_pk = request.POST.get("menuitem")
        quantity = request.POST.get("quantity")

        menu_item = get_object_or_404(MenuItem, pk=item_pk)
        unit_price = menu_item.price
        price = unit_price * int(quantity)

        try:
            created_item = Cart.objects.create(
                user=request.user,
                menuitem=menu_item,
                quantity=quantity,
                unit_price=menu_item.price,
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
def order_details(request, pk):
    order = Order.objects.get(pk=pk)

    if request.method == "GET":
        if (
            request.user != order.user
            and not request.user.groups.filter(name="Delivery Crew").exists()
            and not request.user.groups.filter(name="Manager").exists()
            and not request.user.is_superuser
        ):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        order_items = OrderItem.objects.filter(order=order)
        serialized_order_items = OrderItemSerializer(order_items, many=True)

        return Response(serialized_order_items.data, status=status.HTTP_200_OK)

    if request.method == "PUT" or request.method == "PATCH":
        if not request.user.groups.filter(name="Manager").exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serialized_order = OrderSerializer(order, data=request.data, partial=True)
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save()

        return Response(serialized_order.data)

    if request.method == "PATCH":
        pass

    if request.method == "DELETE":
        if not request.user.groups.filter(name="Manager").exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
