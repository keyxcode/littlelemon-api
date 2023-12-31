from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Category, Cart, OrderItem, Order


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]
        read_only_fields = ["slug"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category"]

    def to_representation(self, obj):
        self.fields["category"] = CategorySerializer()
        return super(MenuItemSerializer, self).to_representation(obj)


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id", "user", "menuitem", "quantity", "unit_price", "price"]
        read_only_fields = ["user", "unit_price", "price"]

    def to_representation(self, obj):
        self.fields["menuitem"] = MenuItemSerializer()
        return super(CartSerializer, self).to_representation(obj)


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "status", "total", "date"]
        read_only_fields = ["id", "user", "total", "date"]


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer()

    class Meta:
        model = OrderItem
        fields = ["order", "menuitem", "quantity", "unit_price", "price"]
