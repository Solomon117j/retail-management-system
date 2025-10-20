from django import template

register = template.Library()

@register.filter
def urlencode_exclude(querydict, exclude_keys):
    """
    URL encode a QueryDict while excluding specified keys.
    Usage: {{ request.GET|urlencode_exclude:'page' }}
    """
    if not querydict:
        return ''

    # Convert exclude_keys to a list if it's a string
    if isinstance(exclude_keys, str):
        exclude_keys = [exclude_keys]

    # Create a copy of the querydict and remove excluded keys
    filtered_dict = querydict.copy()
    for key in exclude_keys:
        filtered_dict.pop(key, None)

    # URL encode the remaining parameters using QueryDict's urlencode method
    if filtered_dict:
        return '&' + filtered_dict.urlencode()
    return ''
