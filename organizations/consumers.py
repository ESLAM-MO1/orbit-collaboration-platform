import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import MeetingRoom


class MeetingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """عند اتصال المستخدم بالـ WebSocket"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"meeting_{self.room_name}"

        user = self.scope["user"]

        # رفض الاتصال للمستخدمين الغير مسجلين
        if user.is_anonymous:
            await self.close()
            return

        # التأكد من وجود الـ meeting
        try:
            meeting = await sync_to_async(
                lambda: MeetingRoom.objects.select_related("host").get(room_name=self.room_name)
            )()
        except MeetingRoom.DoesNotExist:
            await self.close()
            return

        # حفظ معلومات المستخدم
        self.is_host = (user.id == meeting.host_id)
        self.username = user.username

        # إضافة المستخدم للـ group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # قبول الاتصال
        await self.accept()

        # إشعار باقي المستخدمين بدخول مستخدم جديد
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_user_joined",
                "username": user.username,
                "is_host": self.is_host
            }
        )

        print(f"✅ {user.username} connected to {self.room_name} (Host: {self.is_host})")

    async def disconnect(self, close_code):
        """عند قطع الاتصال"""
        # إزالة المستخدم من الـ group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ {self.username} disconnected from {self.room_name}")

    async def receive(self, text_data):
        """
        استقبال رسالة من المستخدم (WebRTC signals)
        """
        try:
            data = json.loads(text_data)
            signal_type = data.get('type', 'unknown')
            
            print(f"📨 Received {signal_type} from {self.username}")
            
            # إضافة معلومات المرسل
            data['sender'] = self.username
            
            # إرسال الـ signal لجميع المستخدمين في الـ room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_webrtc_signal",
                    "data": data,
                    "sender_username": self.username
                }
            )
            
            print(f"📤 Broadcasted {signal_type} to room {self.room_name}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Error from {self.username}: {e}")
        except Exception as e:
            print(f"❌ Error in receive from {self.username}: {e}")

    async def broadcast_webrtc_signal(self, event):
        """
        إرسال WebRTC signal للمستخدم
        (هذه الـ method يتم استدعاؤها من group_send)
        """
        data = event['data']
        sender = event.get('sender_username', 'unknown')
        
        # إرسال الـ signal لجميع المستخدمين (بما فيهم المرسل)
        await self.send(text_data=json.dumps(data))
        
        print(f"📬 Sent {data.get('type')} to {self.username} (from {sender})")

    async def broadcast_user_joined(self, event):
        """
        إرسال إشعار بانضمام مستخدم جديد
        """
        await self.send(text_data=json.dumps({
            "type": "user_joined",
            "username": event["username"],
            "is_host": event["is_host"]
        }))
        
        print(f"👤 Notified {self.username} about {event['username']} joining")