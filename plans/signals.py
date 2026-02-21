from django.db.models.signals import post_delete, post_save, m2m_changed
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils import timezone
import datetime as dt
from dateutil.relativedelta import relativedelta

from plans.utils import recalc_event_instance_status


from .models import (Event, EventCompletion, EventInstance, EventStatus, Order,
                     OrderActivity, OrderActivityResponsibility,
                     Protocol, ProtocolActivity,
                     ProtocolActivityResponsibility)


@receiver(m2m_changed, sender=Event.departments.through)
def validate_departments(sender, instance, action, pk_set, **kwargs):
    """
    Проверяет, что у мероприятия есть хотя бы одно подразделение
    после удаления подразделений
    """
    if action == 'post_remove' and instance.departments.count() == 0:
        raise ValidationError("У мероприятия должно быть хотя бы одно подразделение")
    # Или проверять перед удалением (pre_remove)
    if action == 'pre_remove' and instance.departments.count() == len(pk_set):
        raise ValidationError("Невозможно удалить последнее подразделение")


@receiver(post_save, sender=Event)
def create_initial_event_instance(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.schedule_type == 'once' and instance.due_date:
        EventInstance.objects.create(event=instance, due_date=instance.due_date)
    if instance.schedule_type == 'continuous':
        EventInstance.objects.create(event=instance)
    elif instance.schedule_type == 'periodic':
        # Проверяем наличие необходимых данных
        if instance.start_date and instance.period_unit and instance.period_interval:
            due_date = calculate_due_date(
                start_date=instance.start_date,
                period_unit=instance.period_unit,
                period_interval=instance.period_interval
            )
            EventInstance.objects.create(
                event=instance,
                due_date=due_date,
                # start_date=instance.start_date  # сохраняем дату начала для будущих расчетов
            )
        else:
            # Если данных недостаточно, создаем без due_date
            EventInstance.objects.create(event=instance)


def calculate_due_date(start_date, period_unit, period_interval):
    """
    Рассчитывает дату исполнения на основе периода
    """
    if period_unit == 'day':
        return start_date + dt.timedelta(days=period_interval)
    elif period_unit == 'week':
        return start_date + dt.timedelta(weeks=period_interval)
    elif period_unit == 'month':
        return start_date + relativedelta(months=period_interval)
    elif period_unit == 'quarter':
        # 1 квартал = 3 месяца
        return start_date + relativedelta(months=period_interval * 3)
    elif period_unit == 'year':
        return start_date + relativedelta(years=period_interval)
    return start_date


@receiver(m2m_changed, sender=Event.departments.through)
def create_completions_after_departments(sender, instance, action, **kwargs):
    if action != 'post_add':
        return
    instances = instance.instances.all()
    for inst in instances:
        existing = set(
            inst.completions.values_list('department_id', flat=True)
        )
        to_create = [
            EventCompletion(
                instance=inst,
                department=dept
            )
            for dept in instance.departments.exclude(id__in=existing)
        ]
        EventCompletion.objects.bulk_create(to_create)


@receiver(post_save, sender=EventCompletion)
def sync_instance_status(sender, instance, **kwargs):
    recalc_event_instance_status(instance.instance)
