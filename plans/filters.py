import django_filters as df
from django import forms
from django.db.models import OuterRef, Subquery
from django.forms import DateInput, Select
from django.forms.widgets import Select
from django.utils.functional import lazy
from django.db.models import Q

from equipments.models import Department
from users.models import Role
import datetime as dt

from .models import EventInstance, Event, EventStatus, Department, Document


class DocumentFilter(df.FilterSet):
    subject = df.ChoiceFilter(
        choices=lambda: [(s, s) for s in Document.objects.values_list('subject', flat=True).distinct()],
        label='Направление',
    )
    is_complete = df.ChoiceFilter(
        choices=((True, 'Да'), (False, 'Нет')),
        label='Все мероприятия выполнены'
    )

    class Meta:
        model = Document()
        fields = [
            'subject',
            'is_complete',
        ]


class EventInstanceFilter(df.FilterSet):
    department = df.ModelChoiceFilter(
        field_name='event__departments',
        queryset=Department.objects.none(),
        label='Подразделение',
        method='filter_department'
    )
    status = df.ChoiceFilter(
        choices=EventStatus.CHOICES,
        label='Статус экземпляра'
    )
    schedule_type = df.ChoiceFilter(
        field_name='event__schedule_type',
        choices=Event.SCHEDULE_TYPE_CHOICES,
        label='Тип расписания'
    )
    is_archived = df.BooleanFilter(
        field_name='is_archived',
        label='Архивный статус',
        widget=forms.Select(choices=[
            ('', 'Все'),
            ('true', 'Да'),
            ('false', 'Нет')
        ])
    )
    # # Фильтр по датам
    # due_date_from = df.DateFilter(
    #     field_name='due_date',
    #     lookup_expr='gte',
    #     label='Срок с'
    # )

    # due_date_to = df.DateFilter(
    #     field_name='due_date',
    #     lookup_expr='lte',
    #     label='Срок по'
    # )
    # Фильтр по описанию мероприятия
    search = df.CharFilter(
        method='filter_search',
        label='Поиск'
    )

    class Meta:
        model = EventInstance
        fields = ['department', 'status', 'schedule_type', 'is_archived']

    def filter_by_computed_status(self, queryset, name, value):
        """Фильтр по вычисляемому статусу"""
        today = dt.timezone.now().date()

        if value == EventStatus.COMPLETED:
            return queryset.filter(status=EventStatus.COMPLETED)
        elif value == EventStatus.OVERDUE:
            return queryset.filter(
                Q(status__in=[EventStatus.NOT_STARTED, EventStatus.IN_WORK]) &
                Q(due_date__lt=today)
            )
        elif value == EventStatus.DEADLINE:
            return queryset.filter(
                Q(status__in=[EventStatus.NOT_STARTED, EventStatus.IN_WORK]) &
                Q(due_date__gte=today, due_date__lte=today + dt.timedelta(days=3))
            )
        elif value == EventStatus.IN_WORK:
            return queryset.filter(status=EventStatus.IN_WORK)
        elif value == EventStatus.NOT_STARTED:
            return queryset.filter(status=EventStatus.NOT_STARTED)

        return queryset

    def filter_search(self, queryset, name, value):
        """Поиск по описанию мероприятия"""
        return queryset.filter(
            Q(event__description__icontains=value) |
            Q(event__document__title__icontains=value)
        )

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Получаем подразделения из текущей выборки
            if self.queryset.exists():
                department_ids = self.queryset.values_list(
                    'event__departments__id', flat=True
                ).distinct()
                self.filters['department'].queryset = Department.objects.filter(
                    id__in=department_ids
                ).order_by('name')

    def filter_department(self, queryset, name, value):
        return queryset.filter(event__departments=value)
