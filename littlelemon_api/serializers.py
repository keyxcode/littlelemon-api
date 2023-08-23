from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]
        read_only_fields = ["id", "slug"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category"]
        read_only_fields = ["id"]

    def to_representation(self, obj):
        self.fields["category"] = CategorySerializer()
        return super(MenuItemSerializer, self).to_representation(obj)
