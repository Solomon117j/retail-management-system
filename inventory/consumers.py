import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
from .models import InventoryRecord, InventoryAlert

logger = logging.getLogger(__name__)

class InventoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.store_id = self.scope['url_route']['kwargs']['store_id']
        self.room_group_name = f'inventory_store_{self.store_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connection established for store {self.store_id}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for store {self.store_id}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'unknown')

            if message_type == 'get_inventory_status':
                await self.send_inventory_status()
            elif message_type == 'get_alerts':
                await self.send_alerts_status()

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Internal server error'
            }))

    # Send inventory status to WebSocket
    async def send_inventory_status(self):
        inventory_data = await self.get_inventory_data()
        await self.send(text_data=json.dumps({
            'type': 'inventory_status',
            'data': inventory_data
        }, cls=DjangoJSONEncoder))

    # Send alerts status to WebSocket
    async def send_alerts_status(self):
        alerts_data = await self.get_alerts_data()
        await self.send(text_data=json.dumps({
            'type': 'alerts_status',
            'data': alerts_data
        }, cls=DjangoJSONEncoder))

    # Receive message from room group
    async def inventory_update(self, event):
        """Send inventory update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'inventory_update',
            'data': event['data']
        }, cls=DjangoJSONEncoder))

    async def alert_update(self, event):
        """Send alert update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'alert_update',
            'data': event['data']
        }, cls=DjangoJSONEncoder))

    @database_sync_to_async
    def get_inventory_data(self):
        """Get inventory data for the store"""
        try:
            inventory_records = InventoryRecord.objects.filter(
                store_id=self.store_id
            ).select_related('product', 'store')

            data = []
            for record in inventory_records:
                data.append({
                    'id': record.id,
                    'product_id': record.product.id,
                    'product_name': record.product.name,
                    'sku': record.product.sku,
                    'quantity': record.quantity,
                    'reorder_level': record.product.reorder_level,
                    'location': record.location,
                    'batch_number': record.batch_number,
                    'expiration_date': record.expiration_date,
                    'cost_price': str(record.cost_price) if record.cost_price else None,
                    'last_updated': record.updated_at,
                    'is_low_stock': record.quantity <= record.product.reorder_level,
                    'is_out_of_stock': record.quantity <= 0,
                })

            return data
        except Exception as e:
            logger.error(f"Error getting inventory data: {e}")
            return []

    @database_sync_to_async
    def get_alerts_data(self):
        """Get alerts data for the store"""
        try:
            alerts = InventoryAlert.objects.filter(
                inventory_record__store_id=self.store_id,
                status='ACTIVE'
            ).select_related('inventory_record', 'inventory_record__product')

            data = []
            for alert in alerts:
                data.append({
                    'id': alert.id,
                    'alert_type': alert.alert_type,
                    'alert_type_display': alert.get_alert_type_display(),
                    'priority': alert.priority,
                    'message': alert.message,
                    'product_name': alert.inventory_record.product.name,
                    'current_value': alert.current_value,
                    'threshold_value': alert.threshold_value,
                    'created_at': alert.created_at,
                })

            return data
        except Exception as e:
            logger.error(f"Error getting alerts data: {e}")
            return []
