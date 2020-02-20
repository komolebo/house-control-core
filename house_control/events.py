from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .settings import CHANNEL_GROUP_NAME


class Notification:
    SENSOR_LIST_CHANGED = 'sensor_list_changed'



def send_event_to_front(data):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        CHANNEL_GROUP_NAME, {
            'type': 'send_msg_to_front',
            'message': data
        }
    )

