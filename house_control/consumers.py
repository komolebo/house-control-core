from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from rest_framework.utils import json

from house_control.settings import CHANNEL_GROUP_NAME


class EventConsumer(WebsocketConsumer):

    def connect(self):
        layer = get_channel_layer()

        async_to_sync(self.channel_layer.group_add)(
            CHANNEL_GROUP_NAME,
            self.channel_name
        )
        self.accept()
        print('Group {} connected to {}'.format(CHANNEL_GROUP_NAME, layer))

    def disconnect(self, code):
        layer = get_channel_layer()
        async_to_sync(layer.group_discard)(
            CHANNEL_GROUP_NAME,
            self.channel_name
        )
        print('Group {} disconnected'.format(CHANNEL_GROUP_NAME))

    def receive(self, text_data=None, bytes_data=None):
        print('Message {} received'.format(text_data))
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            CHANNEL_GROUP_NAME, {
                "type": 'send_msg_to_front',
                "message": message
            }
        )

    def send_msg_to_front(self, event):
        message = event['message']

        async_to_sync(self.send(text_data=json.dumps({
            'message': message
        })))
        print('sent "{}" to front'.format(message))
