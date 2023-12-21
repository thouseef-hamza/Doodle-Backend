import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            return
        self.first_name = user.first_name
        async_to_sync(self.channel_layer.group_add)(self.first_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        # Leave
        async_to_sync(self.channel_layer.group_discard)(
            self.first_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        print(text_data) 
        data = json.loads(text_data)
        message = data["message"]
        print(message)
        await self.send(text_data=json.dumps({"message": message}))

    def send(self, text_data=None, bytes_data=None, close=False):
        print(text_data)
        return super().send(text_data, bytes_data, close)
    
    
