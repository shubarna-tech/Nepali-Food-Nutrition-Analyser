# File: myproject/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Your app’s pages: dashboard, scan, history, cheat-day
    path("", include("myapp.urls")),
    path("api/", include("myapp.urls")),
    # Django built-in auth (login/logout, password reset, etc.)
    path("accounts/", include("django.contrib.auth.urls")),
    # Admin site
    path("admin/", admin.site.urls),
]
