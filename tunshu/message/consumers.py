from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

from custom_user.models import User
from message.models import Notification


class MainConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('chat', self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard('chat', self.channel_name)
        await self.close()

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        text_data_json = json.loads(text_data)

        from_user_id = text_data_json.get('from_uid', None)
        to_user_id = text_data_json.get('to_uid', None)
        content = text_data_json.get('content', None)
        if not from_user_id or not to_user_id:
            await self.send(text_data="缺少参数")

        is_agree = content.get('is_agree', None)
        if is_agree:
            from_user = User.objects.get(id=from_user_id)
            content.update({'contact': {'qq': from_user.qq, 'weixin': from_user.weixin, 'phone': from_user.phone}})

        new_notify = Notification.objects.create(from_user_id=from_user_id, to_user_id=to_user_id, content=content)

        await self.channel_layer.group_send('chat',
                                            {
                                                'from_uid': from_user_id,
                                                'to_uid': to_user_id,
                                                'content': text_data_json.get('content', None),
                                                'created': str(new_notify.created),
                                                'type': 'chat.message'
                                            })

    async def chat_message(self, event):
        await self.send_json(
            {
                'from_uid': event['from_uid'],
                'to_uid': event['to_uid'],
                'content': event['content'],
                'created': event['created']
            }
        )