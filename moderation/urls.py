from django.urls import path

from moderation.views import *

app_name = "moderation"

urlpatterns = [
    path("logs/", show_logs, name="show_logs"),
]