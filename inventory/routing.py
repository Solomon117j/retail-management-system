from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/inventory/(?P<store_id>\d+)/$', consumers.InventoryConsumer.as_asgi()),
]
