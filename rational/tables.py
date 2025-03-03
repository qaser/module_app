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
        verbose_name='КС',
        accessor='equipment__get_ks',
    )
    equipment = tables.Column(verbose_name='Подразделение')
    is_economy = tables.BooleanColumn(verbose_name='Эк. эфф.')
    status = tables.Column(empty_values=(), verbose_name='Статус')

    class Meta:
        model = Proposal
        fields = [
            'reg_num',
            'reg_date',
            'title',
            'authors',
            'equipment',
            'category',
            'is_economy',
            'economy_size',
            'status',
        ]
        attrs = {'class': 'table table_rational'}
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
        """Отображение значения КС"""
        ks = record.get_ks()
        return ks.name if ks else '-'

    def order_ks(self, queryset, is_descending):
        """Сортировка по корневому элементу второго уровня"""
        queryset = queryset.annotate(
            ks_name=Subquery(
                Equipment.objects.filter(
                    tree_id=OuterRef('equipment__tree_id'),
                    level=1
                ).values('name')[:1]
            )
        )
        queryset = queryset.order_by('-ks_name' if is_descending else 'ks_name')
        return queryset, True

    def render_status(self, record):
        """Отображение последнего статуса"""
        latest_status = record.statuses.order_by('-date_changed').first()
        return latest_status.get_status_display() if latest_status else 'Нет статуса'

    def render_reg_date(self, value):
        """Отображение даты без времени"""
        return value.strftime('%d.%m.%Y') if value else '-'
