from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name = "home"),
    path("whiteboard/<str:id>", views.whiteboard, name = "whiteboard"),
]


