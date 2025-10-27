import django_tables2 as tables

from users.models import Role

from .models import Diagnostics, PipeDepartment, Repair, Tube


class TubeTable(tables.Table):
    pipe = tables.Column(verbose_name='Участок')
    tube_num = tables.Column(verbose_name='Номер трубы')
    last_diameter = tables.Column(verbose_name='Диаметр, мм')
    last_length = tables.Column(verbose_name='Длина, м')
    last_thickness = tables.Column(verbose_name='Толщина, мм')
    last_type = tables.Column(verbose_name='Тип трубы')
    last_version_date = tables.DateColumn(verbose_name='Дата состояния')

    class Meta:
        model = Tube
        fields = [
            'pipe',
            'tube_num',
            'last_diameter',
            'last_length',
            'last_thickness',
            'last_type',
            'last_version_date',
        ]
        attrs = {'class': 'table table_pipelines'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    # def render_department_root(self, record):
    #     departments = record.pipe.pipedepartment_set.select_related('department')
    #     roots = [pd.department.get_root().name for pd in departments if pd.department]
    #     return ' / '.join(sorted(set(roots))) if roots else '—'


class RepairTable(tables.Table):
    department_root = tables.Column(verbose_name='Филиал', accessor='pk')
    pipeline = tables.Column(verbose_name='Газопровод', accessor='pk')
    object_type = tables.Column(verbose_name='Тип объекта', accessor='pk')
    object_name = tables.Column(verbose_name='Наименование объекта', accessor='pk')
    start_date = tables.DateColumn(verbose_name='Начало ремонта')
    end_date = tables.DateColumn(verbose_name='Окончание ремонта')

    class Meta:
        model = Repair
        fields = [
            'department_root',
            'object_type',
            'pipeline',
            'object_name',
            'start_date',
            'end_date'
        ]
        attrs = {'class': 'table table_pipelines'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    def render_pipeline(self, record):
        if record.pipe:
            return record.pipe.pipeline.title
        if record.node:
            if record.node.node_type == 'bridge' and record.node.sub_pipeline:
                return f'{record.node.pipeline.title}  /  {record.node.sub_pipeline.title}'
            return record.node.pipeline.title
        return '—'

    def render_department_root(self, record):
        if record.pipe:
            pd_list = PipeDepartment.objects.filter(pipe=record.pipe).select_related('department')
            roots = [pd.department.get_root().name for pd in pd_list if pd.department]
            return ' / '.join(sorted(set(roots))) if roots else '—'

        if record.node:
            departments = record.node.equipment.departments.all()
            if departments.exists():
                roots = [d.get_root().name for d in departments]
                return ' / '.join(sorted(set(roots)))
        return '—'

    def render_object_type(self, record):
        if record.pipe:
            return 'Участок газопровода'
        if record.node:
            return record.node.get_node_type_display()
        return '—'

    def render_object_name(self, record):
        if record.pipe:
            return str(record.pipe)
        if record.node:
            return str(record.node)
        return '—'


class DiagnosticsTable(tables.Table):
    department_root = tables.Column(verbose_name='Филиал', accessor='pk')
    pipeline = tables.Column(verbose_name='Газопровод', accessor='pk')
    object_type = tables.Column(verbose_name='Тип объекта', accessor='pk')
    object_name = tables.Column(verbose_name='Наименование объекта', accessor='pk')
    start_date = tables.DateColumn(verbose_name='Начало ВТД')
    end_date = tables.DateColumn(verbose_name='Окончание ВТД')

    class Meta:
        model = Diagnostics
        fields = [
            'department_root',
            'object_type',
            'pipeline',
            'object_name',
            'start_date',
            'end_date'
        ]
        attrs = {'class': 'table table_pipelines'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    def render_pipeline(self, record):
        if record.pipe:
            return record.pipe.pipeline.title
        if record.node:
            if record.node.node_type == 'bridge' and record.node.sub_pipeline:
                return f'{record.node.pipeline.title}  /  {record.node.sub_pipeline.title}'
            return record.node.pipeline.title
        return '—'

    def render_department_root(self, record):
        if record.pipe:
            pd_list = PipeDepartment.objects.filter(pipe=record.pipe).select_related('department')
            roots = [pd.department.get_root().name for pd in pd_list if pd.department]
            return ' / '.join(sorted(set(roots))) if roots else '—'

        if record.node:
            departments = record.node.equipment.departments.all()
            if departments.exists():
                roots = [d.get_root().name for d in departments]
                return ' / '.join(sorted(set(roots)))
        return '—'

    def render_object_type(self, record):
        if record.pipe:
            return 'Участок газопровода'
        if record.node:
            return record.node.get_node_type_display()
        return '—'

    def render_object_name(self, record):
        if record.pipe:
            return str(record.pipe)
        if record.node:
            return str(record.node)
        return '—'
