# myapp/api_views.py
import datetime

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Nutrition
from .serializers import NutritionSerializer

# Full nutrition table for all foods
FOOD_NUTRITION = {
    "burger": {"calories": 500, "protein": 25, "fat": 22, "carbs": 45, "fiber": 3},
    "chiya": {"calories": 120, "protein": 2, "fat": 4, "carbs": 18, "fiber": 0},
    "dalbhat": {"calories": 450, "protein": 12, "fat": 8, "carbs": 80, "fiber": 5},
    "friedrice": {"calories": 300, "protein": 7, "fat": 6, "carbs": 50, "fiber": 2},
    "jeri": {"calories": 160, "protein": 2, "fat": 5, "carbs": 32, "fiber": 1},
    "momo": {"calories": 300, "protein": 12, "fat": 10, "carbs": 38, "fiber": 2},
    "omelette": {"calories": 150, "protein": 10, "fat": 12, "carbs": 2, "fiber": 0},
    "pakoda": {"calories": 180, "protein": 5, "fat": 10, "carbs": 20, "fiber": 2},
    "panipuri": {"calories": 100, "protein": 3, "fat": 2, "carbs": 18, "fiber": 1},
    "pizza": {"calories": 285, "protein": 12, "fat": 10, "carbs": 36, "fiber": 2},
    "roti": {"calories": 120, "protein": 3, "fat": 1, "carbs": 25, "fiber": 2},
    "samosa": {"calories": 150, "protein": 4, "fat": 8, "carbs": 18, "fiber": 2},
    "selroti": {"calories": 200, "protein": 3, "fat": 6, "carbs": 36, "fiber": 1},
    "yomari": {"calories": 250, "protein": 4, "fat": 5, "carbs": 48, "fiber": 2},
    "chatamari": {"calories": 180, "protein": 5, "fat": 4, "carbs": 32, "fiber": 1},
    "chhoila": {"calories": 280, "protein": 20, "fat": 18, "carbs": 6, "fiber": 1},
    "dhindo": {"calories": 300, "protein": 6, "fat": 2, "carbs": 60, "fiber": 4},
    "gundruk": {"calories": 65, "protein": 3, "fat": 0, "carbs": 14, "fiber": 5},
    "kheer": {"calories": 200, "protein": 5, "fat": 6, "carbs": 34, "fiber": 0},
    "sekuwa": {"calories": 250, "protein": 22, "fat": 15, "carbs": 4, "fiber": 1},
}

FOOD_CLASSES = list(FOOD_NUTRITION.keys())


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logs_list(request):
    logs = Nutrition.objects.filter(user=request.user).order_by("-timestamp")
    serializer = NutritionSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def track(request):
    cls = int(request.data.get("class", 0))
    conf = float(request.data.get("confidence", 0.0))
    food_name = FOOD_CLASSES[cls] if 0 <= cls < len(FOOD_CLASSES) else str(cls)
    nutrition = FOOD_NUTRITION.get(
        food_name, {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0}
    )

    Nutrition.objects.create(
        user=request.user,
        food_class=food_name,
        confidence=conf,
        calories=nutrition["calories"],
        protein=nutrition["protein"],
        fat=nutrition["fat"],
        carbs=nutrition["carbs"],
        fiber=nutrition["fiber"],
    )
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_analytics_api(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({"error": "Forbidden"}, status=403)
    # Parse filters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    user_id = request.GET.get("user_id")
    food_class = request.GET.get("food_class")
    qs = Nutrition.objects.all()
    if start_date:
        qs = qs.filter(timestamp__date__gte=start_date)
    if end_date:
        qs = qs.filter(timestamp__date__lte=end_date)
    if user_id:
        qs = qs.filter(user__id=user_id)
    if food_class:
        qs = qs.filter(food_class=food_class)
    # User stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users = (
        User.objects.filter(date_joined__gte=start_date).count() if start_date else 0
    )
    # Top foods
    top_foods = list(
        qs.values("food_class")
        .annotate(scan_count=Count("id"))
        .order_by("-scan_count")[:10]
    )
    # Engagement
    total_scans = qs.count()
    avg_scans_per_user = round(total_scans / total_users, 2) if total_users else 0
    # Daily scans
    daily_labels = []
    daily_scans = []
    if start_date and end_date:
        start = parse_date(start_date)
        end = parse_date(end_date)
        if start and end and end >= start:
            days = (end - start).days + 1
            daily_labels = [
                (start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(days)
            ]
            daily_scans = [
                qs.filter(timestamp__date=label).count() for label in daily_labels
            ]
    return Response(
        {
            "total_users": total_users,
            "active_users": active_users,
            "new_users": new_users,
            "top_foods": top_foods,
            "total_scans": total_scans,
            "avg_scans_per_user": avg_scans_per_user,
            "daily_labels": daily_labels,
            "daily_scans": daily_scans,
        }
    )
