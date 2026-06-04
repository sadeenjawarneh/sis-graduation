import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gp_backend.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import apps.chat.routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(
        apps.chat.routing.websocket_urlpatterns
    ),
})