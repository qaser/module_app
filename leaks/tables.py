import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from users.models import Role

# from locations.models import Department
from .models import Leak


class LeakTable(tables.Table):
    direction = tables.Column(
        accessor='location.department.station.direction',
        verbose_name='Структурное подразделение (ЛПУМГ)',
    )

    class Meta:
        model = Leak
        fields = [
            'direction',
            'place',
            'location',
            'specified_location',
            'description',
            'type_leak',
            # 'reason',
            'detection_date',
            'planned_date',
            'fact_date',
            # 'method',
            # 'detector',
            'executor',
            # 'plan_work',
            # 'doc_name',
            'protocol',
            'is_done',
            # 'note'
        ]
        attrs = {'class': 'table table_leaks'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'leaks/leaks_ext/new_table.html'

    def __init__(self, *args, **kwargs):
        user = kwargs['request'].user
        super(LeakTable, self).__init__(*args, **kwargs)
        if (user.profile.role != Role.ADMIN and user.profile.role != Role.MANAGER):
            self.columns.hide('direction')
