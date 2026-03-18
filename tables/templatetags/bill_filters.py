from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_gst(value, arg):
    try:
        return float(value) * 1.05
    except (ValueError, TypeError):
        return 0
