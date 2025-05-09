from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get a value from a dictionary using a key in a template"""
    return dictionary.get(key, {})


@register.filter
def items(dictionary):
    """Return the items of a dictionary for iteration in a template"""
    return dictionary.items()
