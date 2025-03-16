import django_tables2 as tables

from users.models import Role

from .models import AnnualPlan, Proposal


class ProposalTable(tables.Table):
    department_root = tables.Column(
        empty_values=(),
        verbose_name='Филиал',
        accessor='department_root_name',  # Используем аннотацию
    )
    department = tables.Column(verbose_name='Подразделение')
    economy_size = tables.Column(verbose_name='Эк. эфф.')
    status = tables.Column(empty_values=(), verbose_name='Статус')

    class Meta:
        model = Proposal
        fields = [
            'reg_num',
            'reg_date',
            'title',
            'authors',
            'department',
            'department_root',  # Добавляем новую колонку
            'category',
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
            self.sequence = ['department_root'] + [col for col in self.sequence if col != 'department_root']
        else:
            self.exclude = ('department_root',)  # Скрываем колонку

    def render_department_root(self, value):
        """Отображение корневого оборудования"""
        return value if value else '-'

    def render_status(self, record):
        """Отображение последнего статуса"""
        latest_status = record.statuses.order_by('-date_changed').first()
        return latest_status.get_status_display() if latest_status else 'Нет статуса'

    def render_reg_date(self, value):
        """Отображение даты без времени"""
        return value.strftime('%d.%m.%Y') if value else '-'


class AnnualPlanTable(tables.Table):
    department = tables.Column(verbose_name='Филиал')
    total_proposals = tables.Column(verbose_name='Плановое количество РП')
    completed_proposals = tables.Column(
        verbose_name='Факт. количество РП',
        accessor='completed_proposals'
    )
    percentage_complete = tables.Column(
        verbose_name='Выполнения плана по количеству РП',
        empty_values=()
    )
    total_economy = tables.Column(verbose_name='Плановая эк. эфф., руб.')
    sum_economy = tables.Column(
        verbose_name='Факт. эк. эфф., руб.',
        accessor='sum_economy'
    )
    percentage_economy = tables.Column(
        verbose_name='Выполнения плана эк. эфф.',
        empty_values=()
    )

    class Meta:
        model = AnnualPlan
        fields = [
            'department',
            'year',
            'total_proposals',
            'completed_proposals',
            'percentage_complete',
            'total_economy',
            'sum_economy',
            'percentage_economy',
        ]
        attrs = {'class': 'table table_rational'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    def render_department(self, value):
        return value.name if value else ''

    def render_percentage_complete(self, record):
        if record.total_proposals:
            return f'{(record.completed_proposals / record.total_proposals * 100):.1f}%'
        return '0%'

    def render_percentage_economy(self, record):
        if record.total_economy:
            return f'{(record.sum_economy / record.total_economy * 100):.1f}%'
        return '0%'
