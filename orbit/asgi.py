import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# لازم الأول
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orbit.settings")

# لازم قبل أي import لموديلات أو routing
django.setup()

# بعد كده بس نعمل import
import organizations.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            organizations.routing.websocket_urlpatterns
        )
    ),
})
