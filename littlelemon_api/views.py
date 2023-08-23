from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import generics, status
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, MenuItemSerializer, CategorySerializer
from .permissions import IsManager, IsDeliveryCrew
from .models import MenuItem, Category


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
    search_fields = ["title", "category__title"]

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            permission_classes = []
        elif self.action == "create":
            permission_classes = [IsAdminUser | IsManager]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
