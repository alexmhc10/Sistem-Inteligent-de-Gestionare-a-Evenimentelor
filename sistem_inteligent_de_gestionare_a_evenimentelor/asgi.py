import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from base import consumers  # Asigură-te că ai creat corect consumers.py

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistem_inteligent_de_gestionare_a_evenimentelor.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Rutele pentru HTTP (site-ul tău)
    
    # Rutele pentru WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),  # Rutele pentru chat prin WebSocket
            ]
        )
    ),
})
