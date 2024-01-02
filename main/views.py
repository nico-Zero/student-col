from django.shortcuts import render, redirect
from .forms import (
    GenerateWhiteboardForm,
    DeleteCurrentWhiteboardForm,
    LoginForm,
    RegisterForm,
    EditProfileForm,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Board, Profile



def landingPage(request):
    return render(request,"landing.html")


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("main:home")

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist.")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main:home")
        else:
            messages.error(request, "Username or Password is incorrect.")

    login_form = LoginForm()
    context = {"login_form": login_form}
    return render(request, "login.html", context=context)


def registerPage(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            user_profile = Profile(user=user)
            user_profile.save()
            login(request, user)
            return redirect("main:home")
        else:
            messages.error(request, "An error occurred while registration process.")
            
    register_form = RegisterForm()
    context = {"register_form":register_form}
    return render(request, "register.html", context=context)


@login_required(login_url="main:login")
def logoutPage(request):
    logout(request)
    return redirect("main:login")


@login_required(login_url='main:login')
def profilePage(request, pk):
    profile = Profile.objects.get(user=User.objects.get(pk=pk))
    context = {"profile": profile}
    return render(request, "profile.html", context=context)


@login_required(login_url='main:login')
def editProfilePage(request):
    profile = Profile.objects.get(user=request.user)
    edit_profile_form = EditProfileForm(instance=profile)
    if request.method == "POST":
        edit_profile_form = EditProfileForm(request.POST)
        if edit_profile_form.is_valid():
            new_profile = edit_profile_form.save(commit=False)
            profile.about = new_profile.about
            profile.save()
            return redirect("main:profile", profile.pk)

    context = {
        "profile": profile,
        "edit_profile_form": edit_profile_form,
    }

    return render(
        request,
        "edit_profile.html",
        context=context,
    )


@login_required(login_url="main:login")
def home(request):
    generate_whiteboard_form = GenerateWhiteboardForm()
    generated_whiteboard_url: str = ""
    if request.method == "POST":
        generate_whiteboard_form = GenerateWhiteboardForm(request.POST)
        if generate_whiteboard_form.is_valid():
            board = Board.objects.create(host=request.user)
            url = reverse("main:whiteboard", kwargs={"id": board.id})
            generated_whiteboard_url = request.build_absolute_uri(url)
    context = {
        "generate_whiteboard_form": generate_whiteboard_form,
        "generated_whiteboard_url": generated_whiteboard_url,
    }

    return render(request, "home.html", context=context)


@login_required(login_url="main:login")
def whiteboard(request, id):
    delete_form = DeleteCurrentWhiteboardForm()
    try:
        board = Board.objects.get(id=id)
        if request.method == "POST":
            delete_form = DeleteCurrentWhiteboardForm(request.POST)
            if delete_form.is_valid():
                board.delete()
                return redirect("main:home")

    except Exception as e:
        print("Error:- ", e)
        return redirect("main:home")

    context = {
        "board_id": id,
        "host_pk": board.host.pk,
        "delete_form": delete_form,
    }
    return render(request, "whiteboard.html", context=context)
