from django.urls import re_path

from .consumers import BoardConsumer

# test_routing link = http://127.0.0.1:8000/whiteboard/4af0fb3a-b516-40cf-a60f-64cbe7a1112e

websocket_urlpatterns = [
    re_path(r"board/(?P<board_id>[^/]+)$", BoardConsumer.as_asgi()),
]
