import django_tables2 as tables
from django.db.models import OuterRef, Subquery
from django.urls import reverse
from django.utils.html import format_html

from equipments.models import Equipment
from users.models import Role

from .models import Proposal


class ProposalTable(tables.Table):
    ks = tables.Column(
        empty_values=(),
        # orderable=True,
        verbose_name='КС',
        accessor='equipment__get_ks',
    )
    equipment = tables.Column(verbose_name='Подразделение')

    class Meta:
        model = Proposal
        fields = [
            'ks',
            'reg_num',
            'reg_date',
            'authors',
            'equipment',
            'category',
            'title',
            'is_economy',
            'is_apply',
            'apply_date',
        ]
        attrs = {'class': 'table table_rational'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Извлекаем пользователя из аргументов
        super().__init__(*args, **kwargs)

        # Если пользователь не администратор, удаляем колонку "КС"
        if user and user.role != Role.ADMIN:
            del self.base_columns['ks']

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
