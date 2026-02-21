# your_app/templatetags/query_transform.py
from django import template

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    """
    Создаёт новую строку запроса, сохраняя существующие параметры.
    Пример: ?status=open&department=2 → при page=2 → ?status=open&department=2&page=2
    """
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        else:
            updated.pop(key, None)
    return updated.urlencode()
