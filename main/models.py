from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django_mysql.models.fields.lists import ListCharField
import uuid

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = RichTextField(default="No About...")
    avatar = models.ImageField(upload_to="avatars", default="no_picture.png")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username.capitalize()

class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    online_users = ListCharField(
        base_field=models.CharField(max_length=16, default=""),
        size=255,
        max_length=(255 * 17),
        default="",
    )  # type: ignore

    def to_json(self):
        return {
            "objects": [obj.to_json() for obj in self.board_objects.all()],  # type: ignore
            "online_users": [
                User.objects.get(pk=user_pk).username for user_pk in self.online_users
            ],
        }

    def get_online_users(self):
        return {
            "online_users": [
                User.objects.get(pk=user_pk).username for user_pk in self.online_users
            ],
        }

    def __str__(self):
        return str(self.id)


class BoardObject(models.Model):
    class BoardObjectType(models.TextChoices):
        path = "path"

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="board_objects"
    )
    type = models.CharField(choices=BoardObjectType.choices, max_length=16)
    data = models.JSONField(default=dict)

    def to_json(self):
        type = str(self.type)
        return {"type": type, "points": self.data["points"]}

    @classmethod
    def from_json(cls, board_id, object_data):
        board = Board.objects.get(id=board_id)
        object_data = {**object_data}

        return cls(
            board=board,
            type=object_data.pop("type"),
            data=object_data,
        )

    def __str__(self):
        return self.type + " - " + str(self.board.id)
