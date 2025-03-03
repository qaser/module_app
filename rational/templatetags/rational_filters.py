from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def get_ids(list):
    return '|'.join([str(s.id) for s in list])


@register.filter
def get_names(list):
    return '|'.join([s.service_type.name for s in list])
