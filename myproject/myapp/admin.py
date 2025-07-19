# File: myapp/admin.py
from django.contrib import admin

from .models import Log, Nutrition


@admin.register(Nutrition)
class NutritionAdmin(admin.ModelAdmin):
    list_display = ("user", "food_class", "calories", "confidence", "timestamp")
    list_filter = ("food_class", "timestamp")
    search_fields = ("user__username", "food_class")


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "action")


# Allow admin to edit cheat_day fields
from .models import UserGoal


@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "cheat_day",
        "cheat_day_last_changed",
        "calorie_goal",
        "protein_goal",
        "carb_goal",
        "fat_goal",
        "fiber_goal",
        "water_goal",
    )
    list_filter = ("cheat_day",)
    search_fields = ("user__username",)
    readonly_fields = ()
