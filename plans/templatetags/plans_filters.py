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


@register.filter
def abs(value):
    """Возвращает абсолютное значение числа"""
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""

@register.filter
def add_days(value, days):
    """Добавляет дни к дате"""
    from datetime import timedelta
    try:
        return value + timedelta(days=int(days))
    except (TypeError, ValueError):
        return value

@register.filter
def get_item(dictionary, key):
    """Получает элемент из словаря по ключу"""
    return dictionary.get(key)
