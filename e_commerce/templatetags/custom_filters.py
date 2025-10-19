# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def total_price(price, quantity):
    """Calculate total price"""
    try:
        return float(price) * int(quantity)
    except (ValueError, TypeError):
        return 0

@register.filter
def split(value, arg):
    """Split the value by the argument (delimiter)"""
    try:
        return value.split(arg)
    except (AttributeError, TypeError):
        return []
