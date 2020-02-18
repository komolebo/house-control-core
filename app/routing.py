from channels.routing import ProtocolTypeRouter
from house_control.consumers import SensorConsumer

from django.urls.conf import re_path


websocket_urlpatterns = [
    re_path('ws/sensor', SensorConsumer)
]