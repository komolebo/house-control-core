from channels.routing import ProtocolTypeRouter
from house_control.consumers import EventConsumer

from django.urls.conf import re_path


websocket_urlpatterns = [
    re_path('ws/sensor', EventConsumer)
]