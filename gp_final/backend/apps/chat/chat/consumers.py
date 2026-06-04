import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.team_id   = self.scope['url_route']['kwargs']['team_id']
        self.room_name = f'chat_{self.team_id}'
        self.user = await self._get_user_from_token(self._get_token())
        if not self.user:
            await self.close(code=4001); return
        if not await self._is_member():
            await self.close(code=4003); return
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        history = await self._get_history()
        await self.send(text_data=json.dumps({'type': 'history', 'messages': history}))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        t    = data.get('type', 'message')
        if t == 'message':
            text = data.get('text', '').strip()
            if not text: return
            msg = await self._save_message(text)
            await self.channel_layer.group_send(self.room_name, {
                'type': 'chat_message', 'id': msg.id, 'text': msg.text,
                'sender_id': self.user.id, 'sender_name': self.user.display_name,
                'created_at': msg.created_at.isoformat(),
            })
        elif t == 'edit':
            mid = data.get('message_id')
            txt = data.get('text', '').strip()
            if await self._edit_message(mid, txt):
                await self.channel_layer.group_send(self.room_name, {
                    'type': 'chat_edit', 'id': mid, 'text': txt, 'editor_id': self.user.id,
                })
        elif t == 'delete_for_everyone':
            mid = data.get('message_id')
            if await self._delete_message(mid, True):
                await self.channel_layer.group_send(self.room_name, {'type': 'chat_delete', 'id': mid, 'scope': 'everyone'})
        elif t == 'delete_for_me':
            mid = data.get('message_id')
            await self._delete_message(mid, False)
            await self.send(text_data=json.dumps({'type': 'chat_delete', 'id': mid, 'scope': 'me'}))

    async def chat_message(self, e):
        await self.send(text_data=json.dumps({'type':'message','id':e['id'],'text':e['text'],'sender_id':e['sender_id'],'sender_name':e['sender_name'],'created_at':e['created_at']}))
    async def chat_edit(self, e):
        await self.send(text_data=json.dumps({'type':'edit','id':e['id'],'text':e['text'],'editor_id':e['editor_id']}))
    async def chat_delete(self, e):
        await self.send(text_data=json.dumps({'type':'delete','id':e['id'],'scope':e['scope']}))

    def _get_token(self):
        qs = self.scope.get('query_string', b'').decode()
        for p in qs.split('&'):
            if p.startswith('token='): return p[6:]
        return None

    @database_sync_to_async
    def _get_user_from_token(self, token):
        if not token: return None
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from accounts.models import User
            return User.objects.get(id=AccessToken(token)['user_id'])
        except: return None

    @database_sync_to_async
    def _is_member(self):
        from teams.models import Team
        try:
            t = Team.objects.get(pk=self.team_id)
            return t.members.filter(pk=self.user.pk).exists() or t.supervisor == self.user
        except: return False

    @database_sync_to_async
    def _get_history(self):
        from .models import Message
        msgs = Message.objects.filter(team_id=self.team_id, deleted=False).select_related('sender').order_by('-created_at')[:50]
        return [{'id':m.id,'text':m.text,'sender_id':m.sender_id,'sender_name':m.sender.display_name,'edited':m.edited,'created_at':m.created_at.isoformat()} for m in reversed(list(msgs))]

    @database_sync_to_async
    def _save_message(self, text):
        from .models import Message
        return Message.objects.create(team_id=self.team_id, sender=self.user, text=text)

    @database_sync_to_async
    def _edit_message(self, mid, text):
        from .models import Message
        try:
            m = Message.objects.get(pk=mid, sender=self.user, deleted=False)
            m.text = text; m.edited = True; m.save(update_fields=['text','edited','updated_at']); return True
        except: return False

    @database_sync_to_async
    def _delete_message(self, mid, everyone):
        from .models import Message
        try:
            m = Message.objects.get(pk=mid, sender=self.user)
            if everyone: m.deleted = True; m.save(update_fields=['deleted'])
            else: m.delete()
            return True
        except: return False


class NotificationConsumer(AsyncWebsocketConsumer):
    """ws/notifications/?token=<jwt>  — real-time push for section 11"""

    async def connect(self):
        self.user = await self._get_user_from_token(self._get_token())
        if not self.user:
            await self.close(code=4001); return
        self.group_name = f'notif_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        count = await self._unread_count()
        await self.send(text_data=json.dumps({'type': 'unread_count', 'count': count}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            await self._mark_read()
            await self.send(text_data=json.dumps({'type': 'unread_count', 'count': 0}))

    async def notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification', 'id': event.get('id'),
            'ntype': event.get('ntype'), 'title': event.get('title'), 'message': event.get('message'),
        }))

    def _get_token(self):
        qs = self.scope.get('query_string', b'').decode()
        for p in qs.split('&'):
            if p.startswith('token='): return p[6:]
        return None

    @database_sync_to_async
    def _get_user_from_token(self, token):
        if not token: return None
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from accounts.models import User
            return User.objects.get(id=AccessToken(token)['user_id'])
        except: return None

    @database_sync_to_async
    def _unread_count(self):
        from teams.models import Notification
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def _mark_read(self):
        from teams.models import Notification
        Notification.objects.filter(recipient=self.user, is_read=False).update(is_read=True)
