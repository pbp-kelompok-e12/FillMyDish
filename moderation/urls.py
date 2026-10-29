from django.urls import path

from moderation.views import *

app_name = "moderation"

urlpatterns = [
    path("logs/", show_logs, name="show_logs"),
    path("logs/list", logs_list, name="logs_list"),
    path("logs/<int:log_id>/review/", review, name="review")
]