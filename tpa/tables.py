import django_tables2 as tables
from django.db.models import OuterRef, Subquery
from django.urls import reverse
from django.utils.html import format_html

from equipments.models import Equipment
from users.models import Role

# from locations.models import Department
from .models import Valve


class ValveTable(tables.Table):
    ks = tables.Column(
        empty_values=(),
        # orderable=True,
        verbose_name='КС',
        accessor='equipment__get_ks',
    )
    equipment = tables.Column(verbose_name='Оборудование')
    tech_number = tables.Column(verbose_name='Техн. номер')
    diameter = tables.Column(verbose_name='Диаметр (мм)')
    pressure = tables.Column(verbose_name='Давление (кгс/см²)')
    # factory_number = tables.Column(attrs={'class': 'column-minor'},)
    # year_exploit = tables.Column(attrs={'class': 'column-minor'},)
    # year_made = tables.Column(attrs={'class': 'column-minor'},)
    # drive_factory = tables.Column(attrs={'class': 'column-minor'},)

    class Meta:
        model = Valve
        fields = [
            'ks',
            'equipment',
            'tech_number',
            'title',
            'diameter',
            'pressure',
            'valve_type',
            'factory_number',
            'factory',
            # 'year_made',
            # 'year_exploit',
            'remote',
            'design',
            'drive_type',
            # 'drive_factory',
        ]
        attrs = {'class': 'table table_tpa'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Извлекаем пользователя
        super().__init__(*args, **kwargs)

        if user and user.role == Role.ADMIN:
            # Делаем 'ks' первым, удаляя его из остальных мест
            self.sequence = ['ks'] + [col for col in self.sequence if col != 'ks']
        else:
            self.exclude = ('ks',)  # Скрываем колонку

    def render_ks(self, record):
        ks = record.get_ks()
        return ks.name if ks else '-'

    def order_ks(self, queryset, is_descending):
        # Аннотируем queryset именем корневого элемента второго уровня
        queryset = queryset.annotate(
            ks_name=Subquery(
                Equipment.objects.filter(
                    tree_id=OuterRef('equipment__tree_id'),
                    level=1
                ).values('name')[:1]
            )
        )
        # Сортируем по аннотированному полю
        if is_descending:
            queryset = queryset.order_by('-ks_name')
        else:
            queryset = queryset.order_by('ks_name')
        return (queryset, True)
