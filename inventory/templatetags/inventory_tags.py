from django import template
from django.db.models import Sum
from inventory.models import InventoryRecord

register = template.Library()

@register.simple_tag
def get_stock_status(product):
    """
    Get the stock status for a product across all stores
    Returns: 'in_stock', 'low_stock', 'out_of_stock'
    """
    total_stock = InventoryRecord.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    if total_stock == 0:
        return 'out_of_stock'
    elif total_stock <= product.reorder_level:
        return 'low_stock'
    else:
        return 'in_stock'
