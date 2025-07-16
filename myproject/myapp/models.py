# File: myapp/models.py
from django.conf import settings
from django.db import models


class Nutrition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    calories = models.FloatField()
    protein = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fiber = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_class} ({self.calories} kcal)"


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.action} @ {self.timestamp}"


class UserGoal(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goal"
    )
    calorie_goal = models.PositiveIntegerField(default=2000)
    protein_goal = models.PositiveIntegerField(default=50)  # grams
    carb_goal = models.PositiveIntegerField(default=250)  # grams
    fat_goal = models.PositiveIntegerField(default=70)  # grams
    fiber_goal = models.PositiveIntegerField(default=30)  # grams
    water_goal = models.PositiveIntegerField(default=2000)  # ml
    cheat_day = models.PositiveSmallIntegerField(
        default=4, help_text="0=Monday, 6=Sunday"
    )
    cheat_day_last_changed = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Goals for {self.user}"


class WaterLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.PositiveIntegerField(default=0)  # in ml

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.username} - {self.amount}ml on {self.date}"
