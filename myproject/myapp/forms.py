from django import forms
from .models import UserGoal
from .models import WaterLog


class UserGoalForm(forms.ModelForm):
    class Meta:
        model = UserGoal
        fields = [
            "calorie_goal",
            "protein_goal",
            "carb_goal",
            "fat_goal",
            "fiber_goal",
            "water_goal",
        ]
        widgets = {
            "calorie_goal": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
            "protein_goal": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
            "carb_goal": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
            "fat_goal": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
            "fiber_goal": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
            "water_goal": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
        }


class WaterLogForm(forms.ModelForm):
    class Meta:
        model = WaterLog
        fields = ["amount"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "min": 50,
                    "step": 50,
                    "placeholder": "Amount (ml)",
                }
            ),
        }
