from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .settings import CHANNEL_GROUP_NAME


class Notifications:
    # any sensor data update
    SENSOR_LIST_CHANGED = "sensor_list_changed"


class Events:
    SENSOR_REMOVE = "sensor_remove"
    SENSOR_ADD_REQUEST = "sensor_add_request"


class EventHandler:
    events_data = {}

    @classmethod
    def subscribe(cls, event, callback):
        if not event in cls.events_data:
            cls.events_data[event] = [callback]
        else:
            cls.events_data[event].append(callback)

    @classmethod
    def event(cls, event):
        if event in cls.events_data:
            [callback() for callback in cls.events_data[event]]


def send_event_to_front(notification):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        CHANNEL_GROUP_NAME, {
            'type': 'send_msg_to_front',
            'message': notification
        }
    )
