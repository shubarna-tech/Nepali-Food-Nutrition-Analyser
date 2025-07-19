# File: myapp/api_urls.py
from django.urls import path

from .api_views import admin_analytics_api
from .views import logs_api, track

urlpatterns = [
    path("track/", track, name="api-track"),
    path("logs/", logs_api, name="api-logs"),
    path("admin-analytics/", admin_analytics_api, name="admin-analytics-api"),
]
