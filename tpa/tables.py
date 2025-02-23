import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from users.models import Role

# from locations.models import Department
from .models import Valve


class ValveTable(tables.Table):
    station = tables.Column(
        accessor='location.department.station',
        verbose_name='КС',
    )
    department = tables.Column(
        accessor='location.department',
        verbose_name='Подразделение'
    )

    class Meta:
        model = Valve
        fields = [
            'station',
            'department',
            'location',
            'tech_number',
            'title',
            'diameter',
            'pressure',
            'valve_type',
            'factory',
            'drive_type',
        ]
        attrs = {'class': 'table table_tpa'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'tpa/tpa_ext/new_table.html'
