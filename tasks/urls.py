from django.urls import path
from . import views

urlpatterns = [
    path("ping/", views.ping, name="tasks-ping"),
    path("api/day/", views.day_view, name="tasks-day"),
    path("api/complete/", views.complete_view, name="tasks-complete"),
]
