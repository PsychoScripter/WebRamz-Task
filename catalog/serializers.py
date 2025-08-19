# catalog/serializers.py
from rest_framework import serializers
from catalog.models import Product, Category, Tag
from decimal import Decimal, InvalidOperation

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class PriceField(serializers.DecimalField):
    def to_internal_value(self, data):
        data = str(data).replace(",", "").strip()
        try:
            value = Decimal(data)
        except InvalidOperation:
            raise serializers.ValidationError("Invalid price format")
        return super().to_internal_value(value)

    def to_representation(self, value):
        # if integer
        if value == value.to_integral():
            return "{:,}".format(int(value))  #add ,
        return "{:,}".format(float(value))   # if float


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()  # show category
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    average_rating = serializers.FloatField(read_only=True)
    price = PriceField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "category", "tags", "average_rating"]



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
