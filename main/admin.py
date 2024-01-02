from django.contrib import admin
from .models import Board, BoardObject, Profile

# Register your models here.

admin.site.register(Board)
admin.site.register(BoardObject)
admin.site.register(Profile)
