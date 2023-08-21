from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["title", "price", "featured", "category"]
        depth = 1
