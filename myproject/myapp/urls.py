# File: myapp/urls.py
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views
from .api_views import logs_list, track

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("accounts/login/", views.login_view, name="account_login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("manual-log/", views.manual_log, name="manual_log"),
    path("logs/", logs_list, name="api-logs"),
    path("track/", track, name="api-track"),
    path("scan/", views.scan, name="scan"),
    path("history/", views.history, name="history"),
    path("cheat-day/", views.cheat_day, name="cheat_day"),
    path("goals/", views.user_goal_view, name="user_goal"),
    path("goals/edit/", views.user_goal_update, name="user_goal_update"),
    path("water-log/", views.water_log_view, name="water_log"),
    path(
        "admin/analytics/",
        views.admin_analytics_dashboard,
        name="admin-analytics-dashboard",
    ),
]
