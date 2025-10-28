import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import PurchaseOrder, PurchaseOrderItem

logger = logging.getLogger(__name__)

@receiver(post_save, sender=PurchaseOrder)
def handle_purchase_order_status_change(sender, instance, created, **kwargs):
    """
    Handle purchase order status changes for inventory updates
    """
    if not created and instance.status == 'received':
        # When PO is marked as received, update inventory for all items
        try:
            for item in instance.items.all():
                if item.received_quantity > 0:
                    # Trigger inventory update via the PurchaseOrderItem signal
                    item.save()
        except Exception as e:
            logger.error(f"Error handling PO status change: {e}")

@receiver(pre_save, sender=PurchaseOrderItem)
def track_received_quantity_changes(sender, instance, **kwargs):
    """
    Track changes in received quantity for inventory updates
    """
    if instance.pk:
        try:
            old_instance = PurchaseOrderItem.objects.get(pk=instance.pk)
            if old_instance.received_quantity != instance.received_quantity:
                logger.info(f"Received quantity changed for {instance.product.name}: {old_instance.received_quantity} -> {instance.received_quantity}")
        except PurchaseOrderItem.DoesNotExist:
            pass
