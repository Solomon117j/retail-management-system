from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def urlencode_exclude(querydict, exclude_key):
    """
    URL encode query parameters excluding a specific key
    """
    items = [(k, v) for k, v in querydict.items() if k != exclude_key]
    if items:
        return '&' + urlencode(items)
    return ''

