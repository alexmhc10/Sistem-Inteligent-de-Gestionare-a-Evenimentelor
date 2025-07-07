import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from base import consumers  

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistem_inteligent_de_gestionare_a_evenimentelor.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),  
            ]
        )
    ),
})
