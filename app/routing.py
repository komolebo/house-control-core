from django.conf.urls import url
from django.urls.conf import re_path
from house_control.consumers import EventConsumer

websocket_urlpatterns = [
    re_path('ws/sensors', EventConsumer)
    # url(r"^ws/sensors/$", EventConsumer),
]
