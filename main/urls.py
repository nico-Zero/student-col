from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.landingPage, name="landing"),
    path("home/", views.home, name="home"),
    path("whiteboard/<str:id>", views.whiteboard, name="whiteboard"),
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerPage, name="register"),
    path("logout/", views.logoutPage, name="logout"),
    path("profile/<pk>", views.profilePage, name="profile"),
    path("edit_profile/", views.editProfilePage, name="edit_profile"),
]
