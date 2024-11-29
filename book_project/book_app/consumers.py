import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BookNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'book_notifications'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        print(f"Client connected to group: {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Client disconnected from group: {self.room_group_name}")

    async def receive(self, text_data):
        print("Raw received data:", text_data)
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            print("type of receive fn:", message_type)
            action = text_data_json.get('action')
            book_title = text_data_json.get('book_title')

            if message_type == 'send_notification':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_notification',
                        'action': action,
                        'book_title': book_title
                    }
                )
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
        except Exception as e:
            print("Error processing message:", e)

    async def send_notification(self, event):
        print("event", event)
        try:
            action = event.get("action")
            print("action", action)
            book_title = event.get("book_title")
            print("book_title", book_title)
            if action and book_title:
                message = f"A book titled '{book_title}' has been {action}!"
                await self.send(text_data=json.dumps({
                    'action': action,
                    'book_title': book_title,
                    'message': message
                }))
            else:
                print("Error: Missing action or book title in event.")
        except Exception as e:
            print("Error in send_notification:", e)