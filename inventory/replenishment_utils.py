"""
Replenishment calculation utilities for automated inventory management
"""
import logging
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Avg, Sum, Q
from .models import Product, InventoryRecord, ReplenishmentConfig, StockMovement
from procurement.models import SupplierProduct

logger = logging.getLogger(__name__)


class ReplenishmentCalculator:
    """
    Handles all replenishment calculations including predictive reordering,
    safety stock, and optimal order quantities
    """

    def __init__(self, product, store=None):
        self.product = product
        self.store = store
        self.config = ReplenishmentConfig.get_default_config()

    def calculate_sales_velocity(self, days=30):
        """
        Calculate average daily sales velocity for the product
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get sales movements for the product
        sales_movements = StockMovement.objects.filter(
            product=self.product,
            movement_type='OUT',
            reason='SALE',
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        if self.store:
            sales_movements = sales_movements.filter(store=self.store)

        total_sold = sales_movements.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        velocity = Decimal(total_sold) / Decimal(days)
        return velocity

    def calculate_demand_variability(self, days=90):
        """
        Calculate coefficient of variation for demand (standard deviation / mean)
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get daily sales data
        daily_sales = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            day_sales = StockMovement.objects.filter(
                product=self.product,
                movement_type='OUT',
                reason='SALE',
                created_at__gte=day_start,
                created_at__lte=day_end
            )

            if self.store:
                day_sales = day_sales.filter(store=self.store)

            total_day = day_sales.aggregate(total=Sum('quantity'))['total'] or 0
            daily_sales.append(total_day)

        if not daily_sales:
            return Decimal('0.00')

        # Calculate mean and standard deviation
        mean = sum(daily_sales) / len(daily_sales)
        if mean == 0:
            return Decimal('0.00')

        variance = sum((x - mean) ** 2 for x in daily_sales) / len(daily_sales)
        std_dev = variance ** 0.5
        cv = std_dev / mean

        return Decimal(str(cv)).quantize(Decimal('0.01'))

    def calculate_safety_stock(self):
        """
        Calculate safety stock based on demand variability and lead time
        Safety Stock = Z * σ * √(Lead Time)
        Using simplified formula: Safety Stock = Sales Velocity * Lead Time * Variability Factor
        """
        velocity = self.calculate_sales_velocity()
        variability = self.calculate_demand_variability()

        # Get lead time from supplier
        lead_time = self.get_lead_time()
        if not lead_time:
            lead_time = 7  # Default 7 days

        # Safety stock calculation
        base_safety = velocity * lead_time
        variability_factor = 1 + (variability * self.config.safety_stock_multiplier)

        safety_stock = base_safety * variability_factor
        return max(int(safety_stock), 0)

    def calculate_reorder_point(self):
        """
        Calculate predictive reorder point
        Reorder Point = Safety Stock + (Sales Velocity * Lead Time)
        """
        safety_stock = self.calculate_safety_stock()
        velocity = self.calculate_sales_velocity()
        lead_time = self.get_lead_time() or 7

        reorder_point = safety_stock + int(velocity * lead_time)
        return max(reorder_point, self.product.reorder_level)

    def calculate_optimal_order_quantity(self):
        """
        Calculate Economic Order Quantity (EOQ) or optimal order quantity
        EOQ = √(2DS/H) where D=demand, S=ordering cost, H=holding cost
        Simplified version using sales velocity and supplier minimums
        """
        velocity = self.calculate_sales_velocity()

        # Get supplier information
        supplier_product = self.get_supplier_product()
        if supplier_product:
            min_order = supplier_product.minimum_order_quantity
            # Calculate based on 30 days of sales, but respect minimum order
            optimal = max(int(velocity * 30), min_order)
        else:
            # Fallback to 30 days of sales
            optimal = max(int(velocity * 30), 1)

        return optimal

    def get_lead_time(self):
        """
        Get lead time from preferred supplier
        """
        supplier_product = self.get_supplier_product()
        return supplier_product.lead_time if supplier_product else None

    def get_supplier_product(self):
        """
        Get the preferred supplier product relationship
        """
        try:
            # First try preferred supplier
            preferred = SupplierProduct.objects.filter(
                product=self.product,
                preferred_supplier=True,
                supplier__is_active=True
            ).first()

            if preferred:
                return preferred

            # Fallback to default supplier
            if self.product.default_supplier:
                return SupplierProduct.objects.filter(
                    product=self.product,
                    supplier=self.product.default_supplier
                ).first()

            # Last resort - any active supplier
            return SupplierProduct.objects.filter(
                product=self.product,
                supplier__is_active=True
            ).first()

        except SupplierProduct.DoesNotExist:
            return None

    def should_reorder(self):
        """
        Determine if product should be reordered based on current stock vs reorder point
        """
        current_stock = self.get_current_stock()
        reorder_point = self.calculate_reorder_point()

        return current_stock <= reorder_point

    def get_current_stock(self):
        """
        Get current inventory level for the product
        """
        if self.store:
            inventory = InventoryRecord.objects.filter(
                product=self.product,
                store=self.store
            ).first()
            return inventory.quantity if inventory else 0
        else:
            # Sum across all stores
            total = InventoryRecord.objects.filter(
                product=self.product
            ).aggregate(total=Sum('quantity'))['total'] or 0
            return total

    def get_replenishment_data(self):
        """
        Get comprehensive replenishment data for the product
        """
        return {
            'product': self.product,
            'current_stock': self.get_current_stock(),
            'sales_velocity': self.calculate_sales_velocity(),
            'demand_variability': self.calculate_demand_variability(),
            'safety_stock': self.calculate_safety_stock(),
            'reorder_point': self.calculate_reorder_point(),
            'optimal_order_quantity': self.calculate_optimal_order_quantity(),
            'lead_time': self.get_lead_time(),
            'should_reorder': self.should_reorder(),
            'supplier_product': self.get_supplier_product()
        }


def process_replenishment_batch(store=None):
    """
    Process replenishment batch for products needing reorder.
    Returns the first created batch object.
    """
    processor = BulkReplenishmentProcessor(store)
    products_needing_reorder = processor.get_products_needing_reorder()

    if not products_needing_reorder:
        raise ValueError("No products currently need replenishment")

    supplier_groups = processor.group_by_supplier(products_needing_reorder)
    orders_created = processor.create_bulk_orders(supplier_groups)

    if not orders_created:
        raise ValueError("Failed to create replenishment orders")

    # Return the first batch created
    return orders_created[0]['batch']


class BulkReplenishmentProcessor:
    """
    Handles bulk processing of replenishment for multiple products
    """

    def __init__(self, store=None):
        self.store = store
        self.config = ReplenishmentConfig.get_default_config()

        # Validate that store is a warehouse if provided (only for supplier orders)
        # Note: This validation is now handled in the form level for supplier orders only

    def get_products_needing_reorder(self, criticality_filter=None):
        """
        Get all products that need reordering, optionally filtered by criticality
        """
        products = Product.objects.filter(is_active=True)

        if criticality_filter:
            if isinstance(criticality_filter, list):
                products = products.filter(criticality__in=criticality_filter)
            else:
                products = products.filter(criticality=criticality_filter)

        needing_reorder = []

        for product in products:
            calculator = ReplenishmentCalculator(product, self.store)
            if calculator.should_reorder():
                data = calculator.get_replenishment_data()
                needing_reorder.append(data)

        # Sort by criticality (Critical first, then High, Medium, Low)
        criticality_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        needing_reorder.sort(key=lambda x: criticality_order.get(x['product'].criticality, 4))

        return needing_reorder

    def group_by_supplier(self, replenishment_data):
        """
        Group products by supplier for bulk ordering
        """
        supplier_groups = {}

        for data in replenishment_data:
            supplier_product = data['supplier_product']
            if not supplier_product:
                continue

            supplier = supplier_product.supplier
            if supplier not in supplier_groups:
                supplier_groups[supplier] = []

            supplier_groups[supplier].append(data)

        return supplier_groups

    def create_bulk_orders(self, supplier_groups):
        """
        Create bulk purchase orders for grouped products
        """
        from procurement.models import PurchaseOrder, PurchaseOrderItem
        from inventory.models import ReplenishmentBatch
        from human_resources.models import Employee  # Assuming system user

        orders_created = []

        for supplier, products_data in supplier_groups.items():
            try:
                # Create replenishment batch
                batch_id = f"BATCH-{supplier.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                batch = ReplenishmentBatch.objects.create(
                    batch_id=batch_id,
                    supplier=supplier,
                    store=self.store,
                    status='PENDING',
                    total_items=len(products_data),
                    # created_by=system_user  # TODO: Set system user
                )

                # Create purchase order
                po = PurchaseOrder.objects.create(
                    supplier=supplier,
                    store=self.store,
                    status='draft',
                    replenishment_status='bulk_batch',
                    # created_by=system_user
                )

                total_value = 0
                for data in products_data:
                    product = data['product']
                    quantity = data['optimal_order_quantity']
                    supplier_product = data['supplier_product']

                    # Add item to batch
                    batch.add_item(product, quantity, supplier_product.supply_price)

                    # Add item to PO
                    PurchaseOrderItem.objects.create(
                        order=po,
                        product=product,
                        quantity=quantity,
                        unit_price=supplier_product.supply_price
                    )

                    total_value += quantity * supplier_product.supply_price

                # Update batch with PO reference
                batch.purchase_order = po
                batch.total_value = total_value
                batch.save()

                # Auto-approve if under threshold
                if self.config.auto_approval_enabled and total_value <= self.config.max_auto_approval_amount:
                    po.status = 'auto_approved'
                    po.approved_at = timezone.now()
                    # po.approved_by = system_user
                    po.save()

                    batch.status = 'COMPLETED'
                    batch.completed_at = timezone.now()
                    batch.save()

                orders_created.append({
                    'batch': batch,
                    'purchase_order': po,
                    'items_count': len(products_data),
                    'total_value': total_value
                })

                logger.info(f"Created bulk order batch {batch_id} for {supplier.name}")

            except Exception as e:
                logger.error(f"Error creating bulk order for {supplier.name}: {e}")
                continue

        return orders_created
