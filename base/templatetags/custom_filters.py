from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='replace')
def replace(value, arg):
    return value.replace("_", " ") if isinstance(value, str) else value


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)