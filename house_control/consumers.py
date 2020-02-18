from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from rest_framework.utils import json

class SensorConsumer(WebsocketConsumer):
    def connect(self):
        # async_to_sync(self.channel_layer.group_add) (
        #     "groupname1",
        #     "channelname"
        # )
        self.accept()

    def disconnect(self, code):
        # async_to_sync(self.channel_layer.group_discard)(
        #     "groupname1",
        #     "channelname"
        # )
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
