from django.shortcuts import render, redirect
from .forms import GenerateWhiteboardForm, DeleteCurrentWhiteboardForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Board


# Create your views here.


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


@login_required
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
