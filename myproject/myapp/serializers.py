# File: myapp/serializers.py
from rest_framework import serializers
from .models import Nutrition, Log


class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrition
        fields = ["id", "user", "food_class", "confidence", "calories", "timestamp"]


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ["id", "user", "action", "data", "timestamp"]
