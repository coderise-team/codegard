from apps.realtime.consumers.contest import ContestConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r"^ws/contests/(?P<contest_id>\d+)/$", ContestConsumer.as_asgi()),
]
