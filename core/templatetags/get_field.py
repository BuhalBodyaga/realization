from django import template

register = template.Library()

@register.filter
def get_field(form, name):
    return form[name]