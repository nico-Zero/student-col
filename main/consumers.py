from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import Board, BoardObject
from uuid import uuid4


class BoardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.board_id = self.scope["url_route"]["kwargs"]["board_id"]
        self.session_id = uuid4().hex

        # adding user to board online user list
        board = await sync_to_async(Board.objects.get)(id=self.board_id)
        user = self.scope["user"]
        try:
            await sync_to_async(board.online_users.index)(str(user.pk))
        except:
            if user.is_authenticated:
                await sync_to_async(board.online_users.append)(str(user.pk))
                await sync_to_async(board.save)()
        await self.accept()
        await self.send_initial_data()
        await self.channel_layer.group_add(self.group_name, self.channel_name)  # type: ignore

    @property
    def group_name(self):
        if not self.board_id:
            raise ValueError("No Board Id.")
        return f"board-{self.board_id}"

    async def send_initial_data(self):
        payload = await self.get_board_data()
        return await self.send_json({"type": "INITIAL_DATA", "data": payload})

    @database_sync_to_async
    def get_board_data(self):
        board = Board.objects.get(id=self.board_id)
        payload = board.to_json()
        return payload

    @database_sync_to_async
    def add_object(self, object_data):
        boardObject = BoardObject.from_json(self.board_id, object_data)
        boardObject.save()

    async def receive_json(self, content, **kwargs):
        message_type = content.get("type")
        if message_type == "ADD_OBJECT":
            object_data = content.get("data").get("object")
            board = await sync_to_async(Board.objects.get)(id=self.board_id)
            content["data"] |= await sync_to_async(board.get_online_users)()
            # print(content)
            await self.add_object(object_data)
            await self.channel_layer.group_send(  # type: ignore
                self.group_name,
                {
                    "type": "broadcast.changes",
                    "content": content,
                    "session_id": self.session_id,
                },
            )
        elif message_type == "CLOSED":
            print("CLOSED")
        elif message_type == "GET_USERS":
            board = await sync_to_async(Board.objects.get)(id=self.board_id)
            online_users = await sync_to_async(board.get_online_users)()
            content = {"type": "GET_ONLINE_USERS_RESPONSE", "data": online_users}
            await self.channel_layer.group_send(  # type: ignore
                self.group_name,
                {
                    "type": "broadcast.online.users",
                    "content": content,
                    "session_id": self.session_id,
                },
            )

    async def broadcast_changes(self, event):
        if event.get("session_id") == self.session_id:
            return
        await self.send_json(event["content"])

    async def broadcast_online_users(self, event):
        await self.send_json(event["content"])
        
    async def disconnect(self, close_code):
        try:
            board = await sync_to_async(Board.objects.get)(id=self.board_id)
            user = self.scope["user"]
            await sync_to_async(board.online_users.remove)(str(user.pk))
            await sync_to_async(board.save)()

        except Exception as e:
            print(e)
