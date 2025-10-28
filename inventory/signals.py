import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import InventoryRecord, StockMovement, InventoryAlert, Notification
from sales.models import Sale, SaleItem, Return
from procurement.models import PurchaseOrder, PurchaseOrderItem

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

@receiver(post_save, sender=SaleItem)
def update_inventory_on_sale(sender, instance, created, **kwargs):
    """
    Automatically reduce inventory when a sale item is created
    """
    if created:
        try:
            with transaction.atomic():
                # Get or create inventory record for the product and store
                inventory_record, created = InventoryRecord.objects.get_or_create(
                    product=instance.product,
                    store=instance.sale.store,
                    defaults={'quantity': 0}
                )

                # Reduce inventory quantity
                old_quantity = inventory_record.quantity
                inventory_record.quantity -= instance.quantity
                inventory_record.last_updated_by = instance.sale.employee
                inventory_record.save()

                # Create stock movement record
                StockMovement.objects.create(
                    product=instance.product,
                    store=instance.sale.store,
                    quantity=-instance.quantity,  # Negative for stock out
                    movement_type='OUT',
                    reason='SALE',
                    reference=f"Sale #{instance.sale.id}",
                    created_by=instance.sale.employee
                )

                # Check for alerts after inventory update
                check_inventory_alerts(inventory_record, old_quantity)

                # Send WebSocket update
                send_inventory_update(inventory_record.store.id, 'inventory_update', {
                    'product_id': instance.product.id,
                    'product_name': instance.product.name,
                    'quantity_change': -instance.quantity,
                    'new_quantity': inventory_record.quantity,
                    'movement_type': 'OUT',
                    'reason': 'SALE'
                })

                logger.info(f"Inventory updated for sale: {instance.product.name} -{instance.quantity} at {instance.sale.store.name}")

        except Exception as e:
            logger.error(f"Error updating inventory on sale: {e}")


@receiver(post_save, sender=PurchaseOrderItem)
def update_inventory_on_purchase_receipt(sender, instance, created, **kwargs):
    """
    Automatically increase inventory when purchase order items are received
    """
    # Only update inventory when the purchase order is marked as received
    if instance.order.status == 'received' and instance.received_quantity > 0:
        try:
            with transaction.atomic():
                # Get or create inventory record for the product and store
                inventory_record, created = InventoryRecord.objects.get_or_create(
                    product=instance.product,
                    store=instance.order.store,
                    defaults={'quantity': 0}
                )

                # Increase inventory quantity
                old_quantity = inventory_record.quantity
                inventory_record.quantity += instance.received_quantity
                inventory_record.cost_price = instance.unit_price
                inventory_record.supplier = instance.order.supplier
                inventory_record.save()

                # Create stock movement record
                StockMovement.objects.create(
                    product=instance.product,
                    store=instance.order.store,
                    quantity=instance.received_quantity,
                    movement_type='IN',
                    reason='PURCHASE',
                    reference=f"PO-{instance.order.id}",
                    created_by=instance.order.created_by
                )

                # Check for alerts after inventory update
                check_inventory_alerts(inventory_record, old_quantity)

                # Send WebSocket update
                send_inventory_update(inventory_record.store.id, 'inventory_update', {
                    'product_id': instance.product.id,
                    'product_name': instance.product.name,
                    'quantity_change': instance.received_quantity,
                    'new_quantity': inventory_record.quantity,
                    'movement_type': 'IN',
                    'reason': 'PURCHASE'
                })

                logger.info(f"Inventory updated for purchase receipt: {instance.product.name} +{instance.received_quantity} at {instance.order.store.name}")

        except Exception as e:
            logger.error(f"Error updating inventory on purchase receipt: {e}")


@receiver(post_save, sender=Return)
def update_inventory_on_return(sender, instance, created, **kwargs):
    """
    Automatically increase inventory when items are returned
    """
    if created:
        try:
            with transaction.atomic():
                # Get or create inventory record for the product and store
                inventory_record, created = InventoryRecord.objects.get_or_create(
                    product=instance.sale.items.first().product,  # Get product from sale items
                    store=instance.sale.store,
                    defaults={'quantity': 0}
                )

                # Calculate return quantity from sale items
                return_quantity = sum(item.quantity for item in instance.sale.items.all())

                # Increase inventory quantity
                old_quantity = inventory_record.quantity
                inventory_record.quantity += return_quantity
                inventory_record.save()

                # Create stock movement record
                StockMovement.objects.create(
                    product=inventory_record.product,
                    store=instance.sale.store,
                    quantity=return_quantity,
                    movement_type='IN',
                    reason='RETURN',
                    reference=f"Return #{instance.id}",
                    created_by=instance.employee
                )

                # Check for alerts after inventory update
                check_inventory_alerts(inventory_record, old_quantity)

                # Send WebSocket update
                send_inventory_update(inventory_record.store.id, 'inventory_update', {
                    'product_id': inventory_record.product.id,
                    'product_name': inventory_record.product.name,
                    'quantity_change': return_quantity,
                    'new_quantity': inventory_record.quantity,
                    'movement_type': 'IN',
                    'reason': 'RETURN'
                })

                logger.info(f"Inventory updated for return: {inventory_record.product.name} +{return_quantity} at {instance.sale.store.name}")

        except Exception as e:
            logger.error(f"Error updating inventory on return: {e}")


def check_inventory_alerts(inventory_record, old_quantity):
    """
    Check for inventory alerts based on quantity changes using predictive replenishment
    """
    try:
        from .replenishment_utils import ReplenishmentCalculator

        product = inventory_record.product
        current_quantity = inventory_record.quantity
        calculator = ReplenishmentCalculator(product, inventory_record.store)
        reorder_point = calculator.calculate_reorder_point()
        should_reorder = calculator.should_reorder()

        # Predictive reorder alert
        if should_reorder and current_quantity <= reorder_point:
            optimal_quantity = calculator.calculate_optimal_order_quantity()
            alert, created = InventoryAlert.objects.get_or_create(
                inventory_record=inventory_record,
                alert_type='AUTO_REORDER',
                status='ACTIVE',
                defaults={
                    'priority': 'HIGH',
                    'message': f"Predictive reorder: {product.name} at {current_quantity} units (reorder point: {reorder_point}, suggested order: {optimal_quantity})",
                    'threshold_value': reorder_point,
                    'current_value': current_quantity,
                }
            )
            if created:
                create_notifications_for_alert(alert)
                # Auto-create purchase order if enabled
                from .models import ReplenishmentConfig
                if ReplenishmentConfig.get_default_config().auto_replenishment_enabled:
                    create_auto_purchase_order(inventory_record, optimal_quantity)

        # Out of stock alert
        if current_quantity <= 0 and old_quantity > 0:
            alert, created = InventoryAlert.objects.get_or_create(
                inventory_record=inventory_record,
                alert_type='OUT_OF_STOCK',
                status='ACTIVE',
                defaults={
                    'priority': 'CRITICAL',
                    'message': f"Out of stock alert: {product.name} is completely out of stock",
                    'threshold_value': 0,
                    'current_value': current_quantity,
                }
            )
            if created:
                create_notifications_for_alert(alert)

        # Auto-resolve alerts when stock levels improve
        if current_quantity > reorder_point:
            InventoryAlert.objects.filter(
                inventory_record=inventory_record,
                alert_type__in=['AUTO_REORDER', 'OUT_OF_STOCK'],
                status='ACTIVE'
            ).update(
                status='RESOLVED',
                auto_resolved=True,
                resolved_at=timezone.now()
            )

        # Enhanced expiring soon alerts with configurable thresholds
        if inventory_record.expiration_date:
            days_until_expiry = (inventory_record.expiration_date - timezone.now().date()).days
            config = ExpirationConfig.get_default_config()

            # Check for expired items first
            if days_until_expiry <= 0:
                alert, created = InventoryAlert.objects.get_or_create(
                    inventory_record=inventory_record,
                    alert_type='EXPIRING_SOON',
                    status='ACTIVE',
                    defaults={
                        'priority': 'CRITICAL',
                        'message': f"EXPIRED: {product.name} expired on {inventory_record.expiration_date} ({abs(days_until_expiry)} days ago)",
                        'threshold_value': 0,
                        'current_value': days_until_expiry,
                    }
                )
                if created:
                    create_notifications_for_alert(alert, config)
            else:
                # Check against configurable thresholds
                critical_threshold = config.get_threshold_days('critical')
                warning_threshold = config.get_threshold_days('warning')
                info_threshold = config.get_threshold_days('info')

                alert_priority = None
                threshold_used = None

                if days_until_expiry <= critical_threshold:
                    alert_priority = 'CRITICAL'
                    threshold_used = critical_threshold
                elif days_until_expiry <= warning_threshold:
                    alert_priority = 'HIGH'
                    threshold_used = warning_threshold
                elif days_until_expiry <= info_threshold:
                    alert_priority = 'MEDIUM'
                    threshold_used = info_threshold

                if alert_priority:
                    batch_info = f" (Batch: {inventory_record.batch_number})" if inventory_record.batch_number else ""
                    location_info = f" at {inventory_record.location}" if inventory_record.location else ""

                    alert, created = InventoryAlert.objects.get_or_create(
                        inventory_record=inventory_record,
                        alert_type='EXPIRING_SOON',
                        status='ACTIVE',
                        defaults={
                            'priority': alert_priority,
                            'message': f"Expiring soon: {product.name}{batch_info} expires on {inventory_record.expiration_date} ({days_until_expiry} days remaining){location_info}",
                            'threshold_value': threshold_used,
                            'current_value': days_until_expiry,
                        }
                    )
                    if created:
                        create_notifications_for_alert(alert, config)

        # Legacy auto reorder trigger (fallback for products without predictive data)
        if current_quantity <= product.reorder_level and product.default_supplier and not should_reorder:
            alert, created = InventoryAlert.objects.get_or_create(
                inventory_record=inventory_record,
                alert_type='AUTO_REORDER',
                status='ACTIVE',
                defaults={
                    'priority': 'HIGH',
                    'message': f"Legacy auto reorder: {product.name} needs reordering from {product.default_supplier.name}",
                    'threshold_value': product.reorder_level,
                    'current_value': current_quantity,
                }
            )
            if created:
                create_notifications_for_alert(alert)
                # Trigger automatic purchase order creation
                create_auto_purchase_order(inventory_record)

    except Exception as e:
        logger.error(f"Error checking inventory alerts: {e}")


def create_notifications_for_alert(alert, config=None):
    """
    Create notifications for inventory alerts using configurable recipients
    """
    try:
        from accounts.models import Employee

        # Use config recipients if provided, otherwise default to all relevant departments
        if config and config.notification_recipients:
            recipient_departments = config.notification_recipients
        else:
            recipient_departments = ['Management', 'Inventory', 'Procurement']

        recipients = Employee.objects.filter(
            user__is_active=True,
            department__name__in=recipient_departments
        )

        # Enhanced notification messages based on alert type
        subject = f"Inventory Alert: {alert.get_alert_type_display()}"
        email_message = alert.message
        sms_message = alert.message[:160]  # SMS length limit

        # Add additional context for expiration alerts
        if alert.alert_type == 'EXPIRING_SOON':
            if alert.current_value <= 0:
                subject = f"CRITICAL: EXPIRED PRODUCT - {alert.inventory_record.product.name}"
                email_message += f"\n\nURGENT ACTION REQUIRED: This product has expired and should not be sold."
                sms_message = f"EXPIRED: {alert.inventory_record.product.name} - Remove from sale immediately!"
            elif alert.priority == 'CRITICAL':
                subject = f"CRITICAL: Product Expires Soon - {alert.inventory_record.product.name}"
                email_message += f"\n\nAction Required: Review inventory and prepare for disposal/replacement."
            elif alert.priority == 'HIGH':
                subject = f"WARNING: Product Expires Soon - {alert.inventory_record.product.name}"

        for employee in recipients:
            if employee.user.email:
                Notification.objects.create(
                    alert=alert,
                    notification_type='EMAIL',
                    recipient=employee.user.email,
                    subject=subject,
                    message=email_message
                )

            if employee.phone:
                Notification.objects.create(
                    alert=alert,
                    notification_type='SMS',
                    recipient=employee.phone,
                    message=sms_message
                )

    except Exception as e:
        logger.error(f"Error creating notifications for alert: {e}")


def create_auto_purchase_order(inventory_record, optimal_quantity=None):
    """
    Create automatic purchase order using predictive replenishment calculations
    """
    try:
        from .replenishment_utils import ReplenishmentCalculator

        product = inventory_record.product
        calculator = ReplenishmentCalculator(product, inventory_record.store)
        supplier_product = calculator.get_supplier_product()

        if not supplier_product:
            logger.warning(f"No supplier product relationship for {product.name}, cannot create auto PO")
            return

        supplier = supplier_product.supplier

        # Use provided optimal quantity or calculate it
        if optimal_quantity is None:
            optimal_quantity = calculator.calculate_optimal_order_quantity()

        # Respect minimum order quantity
        order_quantity = max(optimal_quantity, supplier_product.minimum_order_quantity)

        # Check if there's already a pending PO for this product
        existing_po = PurchaseOrder.objects.filter(
            supplier=supplier,
            store=inventory_record.store,
            status__in=['draft', 'pending', 'approved', 'auto_approved'],
            items__product=product
        ).first()

        if existing_po:
            logger.info(f"Pending PO already exists for {product.name}")
            return

        # Check replenishment config for auto-approval
        from .models import ReplenishmentConfig
        config = ReplenishmentConfig.get_default_config()
        order_value = order_quantity * supplier_product.supply_price

        # Create new purchase order
        with transaction.atomic():
            purchase_order = PurchaseOrder.objects.create(
                supplier=supplier,
                store=inventory_record.store,
                status='draft',
                replenishment_status='auto_triggered',
                total_amount=order_value,
                # created_by=None  # System generated
            )

            PurchaseOrderItem.objects.create(
                order=purchase_order,
                product=product,
                quantity=order_quantity,
                unit_price=supplier_product.supply_price
            )

            # Auto-approve if under threshold and enabled
            if config.auto_approval_enabled and order_value <= config.max_auto_approval_amount:
                purchase_order.status = 'auto_approved'
                purchase_order.approved_at = timezone.now()
                # purchase_order.approved_by = system_user
                purchase_order.save()

            # Create stock movement for the auto reorder
            StockMovement.objects.create(
                product=product,
                store=inventory_record.store,
                quantity=order_quantity,
                movement_type='IN',
                reason='AUTO_REORDER',
                reference=f"Auto PO-{purchase_order.id}",
                # created_by=None
            )

            logger.info(f"Predictive auto PO created for {product.name}: {order_quantity} units from {supplier.name} (value: ${order_value:.2f})")

    except Exception as e:
        logger.error(f"Error creating predictive auto purchase order: {e}")


@receiver(pre_save, sender=InventoryRecord)
def check_inventory_changes(sender, instance, **kwargs):
    """
    Check for significant inventory changes before saving
    """
    if instance.pk:
        try:
            old_instance = InventoryRecord.objects.get(pk=instance.pk)
            quantity_change = instance.quantity - old_instance.quantity

            if abs(quantity_change) > 100:  # Significant change threshold
                logger.warning(f"Significant inventory change detected for {instance.product.name}: {quantity_change} units")

        except InventoryRecord.DoesNotExist:
            pass


def send_inventory_update(store_id, event_type, data):
    """
    Send WebSocket update for inventory changes
    """
    try:
        room_group_name = f'inventory_store_{store_id}'
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': event_type,
                'data': data
            }
        )
        logger.debug(f"WebSocket update sent for store {store_id}: {event_type}")
    except Exception as e:
        logger.error(f"Error sending WebSocket update: {e}")


@receiver(post_save, sender=InventoryAlert)
def send_alert_websocket_update(sender, instance, created, **kwargs):
    """
    Send WebSocket update when alerts are created or updated
    """
    if created or instance.status == 'ACTIVE':
        try:
            store_id = instance.inventory_record.store.id
            send_inventory_update(store_id, 'alert_update', {
                'alert_id': instance.id,
                'alert_type': instance.alert_type,
                'alert_type_display': instance.get_alert_type_display(),
                'priority': instance.priority,
                'message': instance.message,
                'product_name': instance.inventory_record.product.name,
                'current_value': instance.current_value,
                'threshold_value': instance.threshold_value,
                'created_at': instance.created_at,
                'status': instance.status,
            })
            logger.debug(f"Alert WebSocket update sent for store {store_id}")
        except Exception as e:
            logger.error(f"Error sending alert WebSocket update: {e}")
