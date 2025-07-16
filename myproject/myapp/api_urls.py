# File: myapp/api_urls.py
from django.urls import path
from .views import track, logs_api
from .api_views import admin_analytics_api

urlpatterns = [
    path("track/", track, name="api-track"),
    path("logs/", logs_api, name="api-logs"),
    path("admin-analytics/", admin_analytics_api, name="admin-analytics-api"),
]
