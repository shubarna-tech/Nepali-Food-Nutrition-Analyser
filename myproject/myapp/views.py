# File: myapp/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone  # ← import this
from .models import Nutrition
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Log
from .serializers import NutritionSerializer, LogSerializer
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from datetime import timedelta, date
from .models import UserGoal, WaterLog
from .forms import UserGoalForm, WaterLogForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import Http404
from django.contrib.auth import get_user_model


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("login"))
    else:
        form = RegistrationForm()
    return render(request, "myapp/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
    else:
        form = AuthenticationForm()
    # Add form-input class to all fields
    for field in form.fields.values():
        field.widget.attrs["class"] = "form-input"
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        return HttpResponseRedirect("/")
    return render(request, "myapp/login.html", {"form": form})


def home(request):
    return render(request, "myapp/home.html")


@login_required
def dashboard(request):
    if request.user.is_superuser or request.user.is_staff:
        return render(request, "myapp/admin_dashboard.html")
    today = timezone.localdate()
    # Fetch all Nutrition entries for request.user with timestamp__date == today
    nutritions = Nutrition.objects.filter(user=request.user, timestamp__date=today)
    total_cal = sum(item.calories for item in nutritions)
    # --- Calculate daily calories for the last 7 days ---
    daily_labels = []
    daily_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        cals = (
            Nutrition.objects.filter(user=request.user, timestamp__date=day).aggregate(
                Sum("calories")
            )["calories__sum"]
            or 0
        )
        daily_labels.append(day.strftime("%a"))
        daily_data.append(int(cals))
    # --- Calculate weekly calories for the last 4 weeks ---
    weekly_labels = []
    weekly_data = []
    for i in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + i * 7)
        week_end = week_start + timedelta(days=6)
        cals = (
            Nutrition.objects.filter(
                user=request.user, timestamp__date__range=(week_start, week_end)
            ).aggregate(Sum("calories"))["calories__sum"]
            or 0
        )
        weekly_labels.append(f"Week {4-i}")
        weekly_data.append(int(cals))
    # --- Calculate monthly calories for the last 4 months ---
    monthly_labels = []
    monthly_data = []
    for i in range(3, -1, -1):
        month = (today.month - i - 1) % 12 + 1
        year = today.year if today.month - i > 0 else today.year - 1
        cals = (
            Nutrition.objects.filter(
                user=request.user, timestamp__year=year, timestamp__month=month
            ).aggregate(Sum("calories"))["calories__sum"]
            or 0
        )
        monthly_labels.append(date(year, month, 1).strftime("%b"))
        monthly_data.append(int(cals))
    # --- Totals for protein, fat, carbs, fiber ---
    total_protein = sum(getattr(item, "protein", 0) for item in nutritions)
    total_fat = sum(getattr(item, "fat", 0) for item in nutritions)
    total_carbs = sum(getattr(item, "carbs", 0) for item in nutritions)
    total_fiber = sum(getattr(item, "fiber", 0) for item in nutritions)
    # --- Macro calories ---
    protein_cals = total_protein * 4
    fat_cals = total_fat * 9
    carb_cals = total_carbs * 4
    macro_total = protein_cals + fat_cals + carb_cals
    macro_carbs_pct = round((carb_cals / macro_total) * 100) if macro_total else 0
    macro_protein_pct = round((protein_cals / macro_total) * 100) if macro_total else 0
    macro_fat_pct = round((fat_cals / macro_total) * 100) if macro_total else 0
    # --- Fiber as percent of total grams (for display only) ---
    macro_grams_total = total_protein + total_fat + total_carbs + total_fiber
    macro_fiber_pct = (
        round((total_fiber / macro_grams_total) * 100) if macro_grams_total else 0
    )

    # Fetch user goals
    user_goal = None
    goal_progress = {}
    goal_percent = {}
    if request.user.is_authenticated:
        user_goal = getattr(request.user, "goal", None)
        if user_goal:
            # Calculate progress for each goal
            goal_progress = {
                "calories": (total_cal, user_goal.calorie_goal),
                "protein": (total_protein, user_goal.protein_goal),
                "carbs": (total_carbs, user_goal.carb_goal),
                "fat": (total_fat, user_goal.fat_goal),
                "fiber": (total_fiber, user_goal.fiber_goal),
                "water": (
                    (total_water, user_goal.water_goal)
                    if "total_water" in locals()
                    else (0, user_goal.water_goal)
                ),
            }

            def percent(val, goal):
                try:
                    return min(int((val / goal) * 100), 100) if goal else 0
                except Exception:
                    return 0

            goal_percent = {
                "calories": percent(
                    goal_progress["calories"][0], goal_progress["calories"][1]
                ),
                "protein": percent(
                    goal_progress["protein"][0], goal_progress["protein"][1]
                ),
                "carbs": percent(goal_progress["carbs"][0], goal_progress["carbs"][1]),
                "fat": percent(goal_progress["fat"][0], goal_progress["fat"][1]),
                "fiber": percent(goal_progress["fiber"][0], goal_progress["fiber"][1]),
                "water": percent(goal_progress["water"][0], goal_progress["water"][1]),
            }

    context = {
        "nutritions": nutritions,
        "total_calories": total_cal,
        "total_protein": int(total_protein),
        "total_fat": int(total_fat),
        "total_carbs": int(total_carbs),
        "total_fiber": int(total_fiber),
        "daily_labels": list(daily_labels),
        "daily_data": list(daily_data),
        "weekly_labels": list(weekly_labels),
        "weekly_data": list(weekly_data),
        "monthly_labels": list(monthly_labels),
        "monthly_data": list(monthly_data),
        "macro_carbs_pct": macro_carbs_pct,
        "macro_protein_pct": macro_protein_pct,
        "macro_fat_pct": macro_fat_pct,
        "macro_fiber_pct": macro_fiber_pct,
        "user_goal": user_goal,
        "goal_progress": goal_progress,
        "goal_percent": goal_percent,
    }
    return render(request, "myapp/dashboard.html", context)


@login_required
def scan(request):
    # Determine if scanning is allowed (not cheat day or in allowed window)
    now = timezone.now()
    is_friday = now.weekday() == 4
    can_scan = True
    if is_friday:
        today = now.date()
        logs = Log.objects.filter(
            user=request.user, action="cheat_window", timestamp__date=today
        ).order_by("-timestamp")
        windows_used = logs.count()
        if windows_used >= 3:
            can_scan = False
        elif logs.exists():
            last = logs.first()
            window_start = last.timestamp
            window_end = window_start + timedelta(hours=2)
            if not (window_start <= now <= window_end):
                can_scan = False
        else:
            can_scan = False
    return render(request, "myapp/scan.html", {"can_scan": can_scan})


@login_required
def history(request):
    logs = Nutrition.objects.filter(user=request.user).order_by("-timestamp")
    # Filtering
    search = request.GET.get("search", "").strip()
    date_filter = request.GET.get("date", "").strip()
    food_type = request.GET.get("food_type", "").strip()
    if search:
        logs = logs.filter(food_class__icontains=search)
    if date_filter:
        logs = logs.filter(timestamp__date=date_filter)
    if food_type:
        logs = logs.filter(food_class=food_type)
    paginator = Paginator(logs, 10)  # Show 10 meals per page
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)
    # Calculate totals
    total_calories = logs.aggregate(Sum("calories"))["calories__sum"] or 0
    total_protein = logs.aggregate(Sum("protein"))["protein__sum"] or 0
    total_fat = logs.aggregate(Sum("fat"))["fat__sum"] or 0
    total_carbs = logs.aggregate(Sum("carbs"))["carbs__sum"] or 0
    total_fiber = logs.aggregate(Sum("fiber"))["fiber__sum"] or 0
    totals = {
        "calories": total_calories,
        "protein": total_protein,
        "fat": total_fat,
        "carbs": total_carbs,
        "fiber": total_fiber,
    }
    # Food type list for dropdown
    from myapp.utils.calorie_table import CALORIE_TABLE

    food_types = sorted(CALORIE_TABLE.keys())
    return render(
        request,
        "myapp/history.html",
        {
            "logs": page_obj,
            "page_obj": page_obj,
            "totals": totals,
            "search": search,
            "date_filter": date_filter,
            "food_type": food_type,
            "food_types": food_types,
        },
    )


@login_required
def cheat_day(request):
    User = get_user_model()
    is_super = request.user.is_superuser
    all_users = None
    selected_user = request.user
    success_message = None
    if is_super:
        all_users = User.objects.all().order_by("username")
        # Get selected user from GET or POST
        selected_user_id = request.GET.get("user_id") or request.POST.get("user_id")
        if selected_user_id:
            try:
                selected_user = User.objects.get(id=selected_user_id)
            except User.DoesNotExist:
                selected_user = request.user
    # Get or create UserGoal for selected user
    user_goal, _ = UserGoal.objects.get_or_create(user=selected_user)
    cheat_day_num = user_goal.cheat_day
    cheat_day_last_changed = user_goal.cheat_day_last_changed
    days_of_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    cheat_day_name = days_of_week[cheat_day_num]
    now = timezone.now()
    today = now.date()
    weekday = now.weekday()
    is_cheat_day = weekday == cheat_day_num
    days_until_next = (cheat_day_num - weekday) % 7
    if days_until_next == 0:
        next_cheat_day = today
    else:
        next_cheat_day = today + timedelta(days=days_until_next)
    can_edit = False
    if cheat_day_last_changed is None:
        can_edit = True
    else:
        last_changed_week = cheat_day_last_changed.isocalendar()[1]
        current_week = today.isocalendar()[1]
        last_changed_year = cheat_day_last_changed.isocalendar()[0]
        current_year = today.isocalendar()[0]
        if (current_year, current_week) > (last_changed_year, last_changed_week):
            can_edit = True
    # Superuser can always edit
    if is_super:
        can_edit = True
    # Handle POST to change cheat day
    if request.method == "POST" and can_edit:
        new_cheat_day = int(request.POST.get("cheat_day", cheat_day_num))
        if 0 <= new_cheat_day <= 6:
            user_goal.cheat_day = new_cheat_day
            user_goal.cheat_day_last_changed = today
            user_goal.save()
            cheat_day_num = new_cheat_day
            cheat_day_name = days_of_week[cheat_day_num]
            is_cheat_day = weekday == cheat_day_num
            days_until_next = (cheat_day_num - weekday) % 7
            if days_until_next == 0:
                next_cheat_day = today
            else:
                next_cheat_day = today + timedelta(days=days_until_next)
            can_edit = False if not is_super else True
            success_message = f"Cheat day updated for {selected_user.username}."
    show_celebration = is_cheat_day
    countdown_seconds = (
        int(
            (next_cheat_day - today).total_seconds()
            + (24 * 60 * 60 - now.hour * 3600 - now.minute * 60 - now.second)
        )
        if not is_cheat_day
        else 0
    )
    context = {
        "status": {
            "is_cheat_day": is_cheat_day,
            "show_celebration": show_celebration,
            "cheat_day_name": cheat_day_name,
            "can_edit": can_edit,
            "cheat_day_num": cheat_day_num,
            "cheat_day_last_changed": cheat_day_last_changed,
            "next_cheat_day": next_cheat_day,
            "countdown_seconds": countdown_seconds,
            "days_of_week": days_of_week,
        },
        "all_users": all_users,
        "selected_user": selected_user,
        "success_message": success_message,
        "is_super": is_super,
    }
    return render(request, "myapp/cheat_day.html", context)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def track(request):
    data = request.data
    nutrition = Nutrition.objects.create(
        user=request.user,
        food_class=data["class"],
        confidence=data["confidence"],
        calories=data.get("calories", 0),
    )
    Log.objects.create(user=request.user, action="track", data=data)
    return Response({"status": "ok", "id": nutrition.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logs_api(request):
    logs = Log.objects.filter(user=request.user).order_by("-timestamp")
    serializer = LogSerializer(logs, many=True)
    return Response(serializer.data)


class ManualMealForm(forms.ModelForm):
    class Meta:
        model = Nutrition
        fields = ["food_class", "calories", "protein", "fat", "carbs", "fiber"]
        widgets = {
            "food_class": forms.TextInput(attrs={"class": "form-input"}),
            "calories": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "protein": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "fat": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "carbs": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "fiber": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
        }


@login_required
def manual_log(request):
    if request.method == "POST":
        form = ManualMealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.confidence = 1.0  # Manual entries are assumed correct
            meal.save()
            return HttpResponseRedirect(reverse("dashboard"))
    else:
        form = ManualMealForm()
    return render(request, "myapp/manual_log.html", {"form": form})


@login_required
def user_goal_view(request):
    message = request.GET.get("msg", "")
    goal, created = UserGoal.objects.get_or_create(user=request.user)
    today = timezone.now().date()
    # Nutrition totals for today
    nutritions = Nutrition.objects.filter(user=request.user, timestamp__date=today)
    total_cal = sum(n.calories for n in nutritions)
    total_protein = sum(n.protein for n in nutritions)
    total_fat = sum(n.fat for n in nutritions)
    total_carbs = sum(n.carbs for n in nutritions)
    total_fiber = sum(n.fiber for n in nutritions)
    # Water intake for today
    water_log, _ = WaterLog.objects.get_or_create(user=request.user, date=today)
    total_water = water_log.amount
    # Progress and percent
    goal_progress = {
        "calories": (total_cal, goal.calorie_goal),
        "protein": (total_protein, goal.protein_goal),
        "carbs": (total_carbs, goal.carb_goal),
        "fat": (total_fat, goal.fat_goal),
        "fiber": (total_fiber, goal.fiber_goal),
        "water": (total_water, goal.water_goal),
    }

    def percent(val, goal):
        try:
            return min(int((val / goal) * 100), 100) if goal else 0
        except Exception:
            return 0

    goal_percent = {k: percent(*v) for k, v in goal_progress.items()}
    # Feedback messages
    feedback = {}
    for k in ["calories", "protein", "carbs", "fat", "fiber"]:
        if goal_progress[k][0] == 0:
            feedback[k] = ""
        elif goal_progress[k][0] < goal_progress[k][1]:
            feedback[k] = (
                f"Keep going! {goal_progress[k][1] - goal_progress[k][0]}g/kcal to reach your goal."
            )
        elif goal_progress[k][0] == goal_progress[k][1]:
            feedback[k] = "🎉 Goal achieved! Great job!"
        else:
            feedback[k] = "⚠️ You have exceeded your goal."
    # Water feedback
    if total_water == 0:
        water_feedback = ""
    elif total_water < goal.water_goal:
        water_feedback = (
            f"Drink {goal.water_goal - total_water}ml more to reach your goal."
        )
    elif total_water == goal.water_goal:
        water_feedback = "💧 Goal achieved! Stay hydrated!"
    else:
        water_feedback = "⚠️ You have exceeded your water goal."
    # Water form
    water_form = WaterLogForm(initial={"amount": 250})
    context = {
        "goal": goal,
        "goal_progress": goal_progress,
        "goal_percent": goal_percent,
        "feedback": feedback,
        "water_feedback": water_feedback,
        "water_form": water_form,
        "total_water": total_water,
        "message": message,
    }
    return render(request, "myapp/user_goal.html", context)


@login_required
def user_goal_update(request):
    goal, created = UserGoal.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("user_goal"))
    else:
        form = UserGoalForm(instance=goal)
    return render(request, "myapp/user_goal_form.html", {"form": form})


@login_required
def water_log_view(request):
    today = timezone.now().date()
    water_log, _ = WaterLog.objects.get_or_create(user=request.user, date=today)
    msg = ""
    if request.method == "POST":
        print("POST data:", request.POST)
        print("Before add: water_log.amount =", water_log.amount)
        form = WaterLogForm(request.POST)
        if form.is_valid():
            add_amount = form.cleaned_data["amount"]
            print("Form valid. Adding:", add_amount)
            water_log.amount += add_amount
            water_log.save()
            print("After add: water_log.amount =", water_log.amount)
            msg = f"Added {add_amount}ml water."
        else:
            print("Form errors:", form.errors)
            msg = "Form error."
    return HttpResponseRedirect(f"{reverse('user_goal')}?msg={msg}")


@login_required
def admin_analytics_dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return render(
            request, "myapp/admin_dashboard.html", {"error": "Access denied."}
        )

    # User stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    from datetime import timedelta
    from django.utils import timezone

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__gte=month_ago).count()

    # Most scanned foods
    top_foods = (
        Nutrition.objects.values("food_class")
        .annotate(scan_count=Count("id"))
        .order_by("-scan_count")[:10]
    )
    top_foods_labels = [f["food_class"].title() for f in top_foods]
    top_foods_data = [f["scan_count"] for f in top_foods]

    # Engagement metrics
    total_scans = Nutrition.objects.count()
    scans_last_7 = Nutrition.objects.filter(timestamp__gte=week_ago).count()
    scans_last_30 = Nutrition.objects.filter(timestamp__gte=month_ago).count()
    avg_scans_per_user = round(total_scans / total_users, 2) if total_users else 0
    # Daily scans for last 7 days
    daily_scans = []
    daily_labels = []
    for i in range(6, -1, -1):
        day = now.date() - timedelta(days=i)
        count = Nutrition.objects.filter(timestamp__date=day).count()
        daily_labels.append(day.strftime("%a"))
        daily_scans.append(count)
    # Weekly retention: users who scanned at least once in last 7 days
    retained_users = (
        Nutrition.objects.filter(timestamp__gte=week_ago)
        .values("user")
        .distinct()
        .count()
    )
    retention_pct = round((retained_users / total_users) * 100, 1) if total_users else 0

    # User growth (new users per day for last 7 days)
    user_growth = []
    for i in range(6, -1, -1):
        day = now.date() - timedelta(days=i)
        count = User.objects.filter(date_joined__date=day).count()
        user_growth.append(count)
    # Scan growth (scans per day for last 7 days)
    scan_growth = []
    for i in range(6, -1, -1):
        day = now.date() - timedelta(days=i)
        count = Nutrition.objects.filter(timestamp__date=day).count()
        scan_growth.append(count)

    # Top 3 Selling Categories (use top_foods as a proxy)
    top_categories = top_foods_labels[:3]
    total_top = sum(top_foods_data[:3]) or 1
    top_categories_percent = [
        round((count / total_top) * 100) for count in top_foods_data[:3]
    ]
    # Most Popular Items (use top_foods as a proxy)
    top_items = [
        {"name": label, "image_url": "/static/myapp/images/logo.png"}
        for label in top_foods_labels[:3]
    ]
    top_items_orders = top_foods_data[:3]

    # Nutrition Analyzer Dashboard Context
    # Top 3 most consumed nutrients (by sum)
    nutrient_totals = Nutrition.objects.aggregate(
        total_calories=Sum("calories"),
        total_protein=Sum("protein"),
        total_fat=Sum("fat"),
        total_carbs=Sum("carbs"),
        total_fiber=Sum("fiber"),
    )
    # Average daily intake per user (last 7 days)
    avg_nutrients = {}
    for field in ["calories", "protein", "fat", "carbs", "fiber"]:
        total = (
            Nutrition.objects.filter(timestamp__gte=week_ago).aggregate(
                total=Sum(field)
            )["total"]
            or 0
        )
        avg_nutrients[field] = round(total / (total_users * 7), 2) if total_users else 0
    # Most common food classes
    common_foods = (
        Nutrition.objects.values("food_class")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )
    common_food_labels = [f["food_class"].title() for f in common_foods]
    common_food_counts = [f["count"] for f in common_foods]
    common_foods_zipped = list(zip(common_food_labels, common_food_counts))
    # Trends for main nutrients (last 7 days)
    trend_labels = []
    trend_calories = []
    trend_protein = []
    trend_fat = []
    trend_carbs = []
    trend_fiber = []
    for i in range(6, -1, -1):
        day = now.date() - timedelta(days=i)
        trend_labels.append(day.strftime("%a"))
        trend_calories.append(
            Nutrition.objects.filter(timestamp__date=day).aggregate(
                total=Sum("calories")
            )["total"]
            or 0
        )
        trend_protein.append(
            Nutrition.objects.filter(timestamp__date=day).aggregate(
                total=Sum("protein")
            )["total"]
            or 0
        )
        trend_fat.append(
            Nutrition.objects.filter(timestamp__date=day).aggregate(total=Sum("fat"))[
                "total"
            ]
            or 0
        )
        trend_carbs.append(
            Nutrition.objects.filter(timestamp__date=day).aggregate(total=Sum("carbs"))[
                "total"
            ]
            or 0
        )
        trend_fiber.append(
            Nutrition.objects.filter(timestamp__date=day).aggregate(total=Sum("fiber"))[
                "total"
            ]
            or 0
        )
    # Ensure all trend variables are lists of length 7
    if len(trend_labels) < 7:
        trend_labels += [""] * (7 - len(trend_labels))
    if len(trend_calories) < 7:
        trend_calories += [0] * (7 - len(trend_calories))
    if len(trend_protein) < 7:
        trend_protein += [0] * (7 - len(trend_protein))
    if len(trend_fat) < 7:
        trend_fat += [0] * (7 - len(trend_fat))
    if len(trend_carbs) < 7:
        trend_carbs += [0] * (7 - len(trend_carbs))
    if len(trend_fiber) < 7:
        trend_fiber += [0] * (7 - len(trend_fiber))

    context = {
        "total_users": total_users,
        "active_users": active_users,
        "new_users_week": new_users_week,
        "new_users_month": new_users_month,
        "top_foods": top_foods,
        "top_foods_labels": top_foods_labels,
        "top_foods_data": top_foods_data,
        "total_scans": total_scans,
        "scans_last_7": scans_last_7,
        "scans_last_30": scans_last_30,
        "avg_scans_per_user": avg_scans_per_user,
        "daily_labels": daily_labels,
        "daily_scans": daily_scans,
        "retention_pct": retention_pct,
        "user_growth": user_growth,
        "scan_growth": scan_growth,
    }
    context.update(
        {
            "top_categories": top_categories,
            "top_categories_percent": top_categories_percent,
            "top_items": top_items,
            "top_items_orders": top_items_orders,
            "nutrient_totals": nutrient_totals,
            "avg_nutrients": avg_nutrients,
            "common_foods": common_foods_zipped,
            "trend_labels": trend_labels,
            "trend_calories": trend_calories,
            "trend_protein": trend_protein,
            "trend_fat": trend_fat,
            "trend_carbs": trend_carbs,
            "trend_fiber": trend_fiber,
        }
    )
    return render(request, "myapp/admin_analytics_dashboard.html", context)
