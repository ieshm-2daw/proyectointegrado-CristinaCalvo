import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Mensaje, Usuario
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f"chat_{self.room_slug}"

        # Agrega el canal al grupo
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()  # Acepta la conexión del WebSocket

    async def disconnect(self, close_code):
        # Remueve el canal del grupo
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)  # Deserializa el JSON
            mensaje = data.get('message', '')
            username = data.get('username', '')

            if mensaje and username:
                # Usa sync_to_async para operaciones síncronas como acceso a la base de datos
                room = await sync_to_async(Room.objects.get)(slug=self.room_slug)
                # Usa el modelo personalizado para obtener el usuario
                usuario = await sync_to_async(Usuario.objects.get)(username=username)

                # Guarda el mensaje en la base de datos de forma asíncrona
                mensaje_obj = await sync_to_async(Mensaje.objects.create)(
                    room=room, 
                    usuario=usuario, 
                    content=mensaje,
                    created_on=timezone.now()  # Agregar la hora actual al crear el mensaje
                )

                # Envía el mensaje a todos en el grupo
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': mensaje,
                        'username': username,
                        'time': mensaje_obj.created_on.strftime('%H:%M'),  # Pasa la hora del mensaje
                    }
                )
        except Exception as e:
            print(f"Error processing message: {e}")

    async def chat_message(self, event):
        mensaje = event.get('message', '')
        username = event.get('username', '')
        time = event.get('time', '')

        if mensaje and username and time:
            # Envía el mensaje a todos los clientes conectados
            await self.send(text_data=json.dumps({
                'message': mensaje,
                'username': username,
                'time': time,
            }))
