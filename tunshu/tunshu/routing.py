from channels.routing import ProtocolTypeRouter, URLRouter
import message.routing

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        message.routing.websocket_urlpatterns
    )
})