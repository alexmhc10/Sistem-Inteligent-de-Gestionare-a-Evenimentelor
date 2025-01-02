from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={'class': css})



@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)