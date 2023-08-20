from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializers import UserSerializer


# Create your views here.
@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def managers(request):
    if request.method == "GET":
        users = User.objects.filter(groups__name="Manager")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        username = request.data["username"]

        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response({"message": "ok"})

    return Response({"message": "error"})
