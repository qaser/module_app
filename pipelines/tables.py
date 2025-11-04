import django_tables2 as tables

from users.models import Role

from .models import (Diagnostics, PipeDepartment, Repair, Tube, TubeUnit,
                     TubeVersion)


class TubeTable(tables.Table):
    pipe = tables.Column(verbose_name='Участок')
    tube_num = tables.Column(verbose_name='Номер элемента')
    last_diameter = tables.Column(verbose_name='Диаметр, мм')
    last_length = tables.Column(verbose_name='Длина, м')
    last_thickness = tables.Column(verbose_name='Толщина, мм')
    last_type = tables.Column(verbose_name='Тип элемента')
    last_steel_grade = tables.Column(verbose_name='Марка стали')
    unit_type = tables.Column(verbose_name='Элемент обустройства', accessor='pk')
    source = tables.Column(verbose_name='Источник информации', accessor='pk')

    class Meta:
        model = Tube
        fields = [
            'pipe',
            'tube_num',
            'last_diameter',
            'last_length',
            'last_thickness',
            'last_type',
            'last_steel_grade',
            'unit_type',
            'source',
        ]
        attrs = {'class': 'table table_pipelines'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    def render_source(self, record):
        # Получаем последнюю версию трубы с предзагрузкой диагностики и ремонта
        latest_version = TubeVersion.objects.filter(
            tube=record
        ).select_related(
            'diagnostics', 'repair'
        ).order_by('-date').first()
        if not latest_version:
            return '-'
        # Проверяем, связана ли версия с диагностикой
        if latest_version.diagnostics:
            diagnostic = latest_version.diagnostics
            start_date_str = diagnostic.start_date.strftime('%d.%m.%Y') if diagnostic.start_date else ''
            end_date_str = diagnostic.end_date.strftime('%d.%m.%Y') if diagnostic.end_date else ''
            return f'ВТД, {start_date_str} - {end_date_str}'
        # Проверяем, связана ли версия с ремонтом
        elif latest_version.repair:
            repair = latest_version.repair
            start_date_str = repair.start_date.strftime('%d.%m.%Y') if repair.start_date else ''
            end_date_str = repair.end_date.strftime('%d.%m.%Y') if repair.end_date else ''
            return f'Ремонт, {start_date_str} - {end_date_str}'
        return '-'

    def render_unit_type(self, record):
        if record.unit_type:
            # Получаем human-readable значение
            for choice in TubeUnit.UNIT_TYPE:
                if choice[0] == record.unit_type:
                    return choice[1]
        return '-'


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
    pipes_distance = tables.Column(verbose_name='Участок газопровода', accessor='pk')
    start_date = tables.DateColumn(verbose_name='Начало ВТД')
    end_date = tables.DateColumn(verbose_name='Окончание ВТД')

    class Meta:
        model = Diagnostics
        fields = [
            'department_root',
            'pipeline',
            'pipes_distance',
            'start_date',
            'end_date'
        ]
        attrs = {'class': 'table table_pipelines'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        template_name = 'module_app/table/new_table.html'

    def render_pipeline(self, record):
        pipelines = set()
        for pipe in record.pipes.all():
            if pipe.pipeline:
                pipelines.add(pipe.pipeline.title)

        if pipelines:
            if len(pipelines) == 1:
                return list(pipelines)[0]
            else:
                return f"Несколько ({len(pipelines)})"
        return '—'

    def render_department_root(self, record):
        all_roots = set()
        for pipe in record.pipes.all():
            for pd in pipe.pipedepartment_set.all():
                if pd.department:
                    root = pd.department.get_root()
                    all_roots.add(root.name)

        if all_roots:
            return ' / '.join(sorted(all_roots))
        return '—'

    def render_pipes_distance(self, record):
        pipes = list(record.pipes.all())
        if pipes:
            if len(pipes) == 1:
                return str(pipes[0])
            else:
                start_points = [pipe.start_point for pipe in pipes]
                end_points = [pipe.end_point for pipe in pipes]
                min_start = min(start_points)
                max_end = max(end_points)
                return f"от {min_start} до {max_end} км"
        return '—'
