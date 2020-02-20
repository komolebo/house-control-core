from django.urls.conf import re_path
from house_control.consumers import EventConsumer

websocket_urlpatterns = [
    re_path('ws/sensor', EventConsumer)
]
