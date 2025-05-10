import django_tables2 as tables
from django.db.models import OuterRef, Subquery

from equipments.models import Equipment
from users.models import Role

from .models import Valve


class ValveTable(tables.Table):
    ks = tables.Column(
        empty_values=(),
        # orderable=True,
        verbose_name='КС',
        accessor='equipment__get_ks',
    )
    root_equipment = tables.Column(
        empty_values=(),
        verbose_name='Место нахождения',
        accessor='get_root_equipment',
        orderable=False
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
            'root_equipment',
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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role == Role.ADMIN:
            self.sequence = ['ks', 'root_equipment'] + [col for col in self.sequence if col not in ['ks', 'root_equipment']]
        else:
            self.sequence = ['root_equipment'] + [col for col in self.sequence if col != 'root_equipment']
            self.exclude = ('ks',)

    def render_root_equipment(self, record):
        root = record.get_root_equipment()
        return root.name if root else '-'

    def get_root_equipment(self, record):
        """Метод для получения корневого оборудования"""
        if record.equipment:
            return record.equipment.get_root()
        return None

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
