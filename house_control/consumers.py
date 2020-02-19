from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from rest_framework.utils import json

class SensorConsumer(WebsocketConsumer):
    GROUP_NAME = "base"
    CHANNEL_NAME = "channel"

    def connect(self):
        self.group_name = self.GROUP_NAME
        self.channel_name = self.CHANNEL_NAME
        self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        self.accept()
        print('Group {} connected'.format(self.group_name))

    def disconnect(self, code):
        self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print('Group {} disconnected'.format(self.group_name))

    def receive(self, text_data=None, bytes_data=None):
        print('____________________message received')
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.channel_layer.group_send(
            self.group_name, {
                "type": 'send_message_to_front',
                "message": message
            }
        )

    def send_message_to_front(self, event):
        print (event)
        message = event['message']
        print('sending {} to front'.format(message))

        self.send(text_data=json.dumps({
            'message': message
        }))
