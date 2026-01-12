import django_filters as df
from django import forms
from django.db.models import Exists, OuterRef, Q, Subquery

from equipments.models import Department
from pipelines.models import (Anomaly, Bend, Diagnostics, Node, Pipe, PipeDepartment,
                              Pipeline, Repair, Tube, TubeUnit, TubeVersion)


def unit_exists(unit_type=None):
    qs = TubeUnit.objects.filter(tube=OuterRef('last_version_id'))
    if unit_type:
        qs = qs.filter(unit_type=unit_type)
    return Exists(qs)


class TubeVersionFilter(df.FilterSet):
    tube_num = df.CharFilter(
        label='Номер элемента',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tube_length = df.NumberFilter(
        lookup_expr='exact',
        label='Длина элемента, м'
    )
    thickness = df.ChoiceFilter(
        label='Толщина стенки (мм)',
        field_name='thickness',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    tube_type = df.ChoiceFilter(
        choices=TubeVersion._meta.get_field('tube_type').choices,
        label='Тип элемента'
    )
    category = df.ChoiceFilter(
        choices=TubeVersion._meta.get_field('category').choices,
        label='Категория'
    )
    steel_grade = df.ChoiceFilter(
        label='Марка стали',
        field_name='steel_grade',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    yield_strength = df.CharFilter(
        lookup_expr='icontains',
        label='Предел текучести стали, МПа'
    )
    tear_strength = df.CharFilter(
        lookup_expr='icontains',
        label='Сопротивление разрыву стали, МПа'
    )

    class Meta:
        model = TubeVersion
        fields = [
            'tube_num',
            'tube_length',
            'thickness',
            'tube_type',
            'category',
            'steel_grade',
            'yield_strength',
            'tear_strength',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = self.queryset
        thickness_values = (
            qs.exclude(thickness__isnull=True)
              .values_list('thickness', flat=True)
              .distinct()
              .order_by('thickness')
        )
        self.filters['thickness'].extra['choices'] = [
            (v, f'{v} мм') for v in thickness_values
        ]
        steel_grades = (
            qs.exclude(steel_grade__isnull=True)
              .exclude(steel_grade='')
              .values_list('steel_grade', flat=True)
              .distinct()
              .order_by('steel_grade')
        )
        self.filters['steel_grade'].extra['choices'] = [
            (v, v) for v in steel_grades
        ]


class TubeUnitFilter(df.FilterSet):
    unit_type = df.ChoiceFilter(
        choices=TubeUnit.UNIT_TYPE,
        method='filter_unit_type',
        label='Тип элемента'
    )

    class Meta:
        model = TubeUnit
        fields = [
            'unit_type',
        ]


class BendFilter(df.FilterSet):
    class Meta:
        model = Bend
        fields = [
            'tube_num',
        ]


class AnomalyFilter(df.FilterSet):
    class Meta:
        model = Anomaly
        fields = [
            'odometr_data',
        ]


class TubeFilter(df.FilterSet):
    tube_num = df.CharFilter(
        label='Номер элемента',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_length = df.ChoiceFilter(
        label='Длина элемента (м)',
        field_name='last_length',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    last_thickness = df.ChoiceFilter(
        label='Толщина стенки (мм)',
        field_name='last_thickness',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    last_type = df.ChoiceFilter(
        label='Тип',
        field_name='last_type',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    last_steel_grade = df.ChoiceFilter(
        label='Марка стали',
        field_name='last_steel_grade',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    unit_type = df.ChoiceFilter(
        label='Элементы обустройства',
        choices=lambda: [
            ('all_units', 'Все элементы обустройства'),
            ('no_units', 'Без элементов обустройства'),
        ] + [
            (val, label) for val, label in TubeUnit.UNIT_TYPE
        ],
        method='filter_unit_type',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Tube
        fields = [
            'tube_num',
            'last_length',
            'last_thickness',
            'last_type',
            'last_steel_grade',
            'unit_type',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = self.queryset
        steel_grades = (
            qs
            .exclude(last_steel_grade__isnull=True)
            .exclude(last_steel_grade='')
            .values_list('last_steel_grade', flat=True)
            .order_by()
            .distinct()
            .order_by('last_steel_grade')
        )
        self.filters['last_steel_grade'].extra['choices'] = [
            (val, val) for val in steel_grades
        ]
        lengths = (
            qs.exclude(last_length__isnull=True)
            .values_list('last_length', flat=True)
            .order_by()
            .distinct()
            .order_by('last_length')
        )
        self.filters['last_length'].extra['choices'] = [
            (v, f'{v} м') for v in lengths
        ]
        thicknesses = (
            qs.exclude(last_thickness__isnull=True)
            .values_list('last_thickness', flat=True)
            .order_by()
            .distinct()
            .order_by('last_thickness')
        )
        self.filters['last_thickness'].extra['choices'] = [
            (v, f'{v} мм') for v in thicknesses
        ]
        types = (
            qs
            .exclude(last_type__isnull=True)
            .exclude(last_type='')
            .order_by()  # <-- КЛЮЧЕВОЕ
            .values_list('last_type', flat=True)
            .distinct()
        )
        self.filters['last_type'].extra['choices'] = [
            (v, dict(TubeVersion.TUBE_TYPE).get(v, v)) for v in types
        ]


    def filter_unit_type(self, queryset, name, value):
        if value == 'all_units':
            return queryset.filter(unit_exists())

        elif value == 'no_units':
            return queryset.exclude(unit_exists())

        else:
            return queryset.filter(unit_exists(value))


class RepairFilter(df.FilterSet):
    STATUS_CHOICES = [
        ('completed', 'Завершён'),
        ('in_progress', 'Не завершён'),
    ]

    pipeline = df.ModelChoiceFilter(
        label='Газопровод',
        queryset=Pipeline.objects.all().order_by('title'),
        method='filter_pipeline'
    )
    department = df.ModelChoiceFilter(
        label='Филиал',
        queryset=Department.objects.filter(level=0).order_by('name'),
        method='filter_department'
    )
    object_type = df.ChoiceFilter(
        label='Тип объекта',
        choices=[
            ('pipe', 'Участок газопровода'),
            ('valve', 'Линейный кран'),
            ('host', 'Узел подключения'),
            ('bridge', 'Перемычка'),
            ('tails', 'Шлейфы'),
            ('ks', 'КС'),
        ],
        method='filter_object_type'
    )
    status = df.ChoiceFilter(
        label='Статус',
        choices=STATUS_CHOICES,
        method='filter_status'
    )
    start_date = df.DateFilter(
        label='Начало ремонта после',
        field_name='start_date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    end_date = df.DateFilter(
        label='Окончание ремонта до',
        field_name='end_date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )

    class Meta:
        model = Repair
        fields = []

    def filter_pipeline(self, queryset, name, value):
        return queryset.filter(
            Q(pipe__pipeline=value) |
            Q(node__pipeline=value) |
            Q(node__sub_pipeline=value)
        )

    def filter_department(self, queryset, name, value):
        return queryset.filter(
            Q(pipe__pipedepartment__department__tree_id=value.tree_id,
                 pipe__pipedepartment__department__level__gte=value.level) |
            Q(node__equipment__departments__tree_id=value.tree_id,
                 node__equipment__departments__level__gte=value.level)
        ).distinct()

    def filter_object_type(self, queryset, name, value):
        if value == 'pipe':
            return queryset.filter(pipe__isnull=False)
        else:
            return queryset.filter(node__node_type=value)

    def filter_status(self, queryset, name, value):
        if value == 'completed':
            return queryset.filter(end_date__isnull=False)
        elif value == 'in_progress':
            return queryset.filter(end_date__isnull=True)
        return queryset


class DiagnosticsFilter(df.FilterSet):
    STATUS_CHOICES = [
        ('completed', 'Завершено'),
        ('in_progress', 'Не завершено'),
    ]

    pipeline = df.ModelChoiceFilter(
        label='Газопровод',
        queryset=Pipeline.objects.all().order_by('title'),
        method='filter_pipeline'
    )
    department = df.ModelChoiceFilter(
        label='Филиал',
        queryset=Department.objects.filter(level=0).order_by('name'),
        method='filter_department'
    )
    status = df.ChoiceFilter(
        label='Статус',
        choices=STATUS_CHOICES,
        method='filter_status'
    )
    start_date = df.DateFilter(
        label='Начало ВТД после',
        field_name='start_date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    end_date = df.DateFilter(
        label='Окончание ВТД до',
        field_name='end_date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    # Дополнительные фильтры для участков
    start_point = df.NumberFilter(
        label='Начало участка от (км)',
        method='filter_start_point',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    end_point = df.NumberFilter(
        label='Конец участка до (км)',
        method='filter_end_point',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Diagnostics
        fields = []

    def filter_pipeline(self, queryset, name, value):
        return queryset.filter(pipes__pipeline=value).distinct()

    def filter_department(self, queryset, name, value):
        return queryset.filter(
            pipes__pipedepartment__department__tree_id=value.tree_id,
            pipes__pipedepartment__department__level__gte=value.level
        ).distinct()

    def filter_status(self, queryset, name, value):
        if value == 'completed':
            return queryset.filter(end_date__isnull=False)
        elif value == 'in_progress':
            return queryset.filter(end_date__isnull=True)
        return queryset

    def filter_start_point(self, queryset, name, value):
        # Фильтруем диагностики, у которых есть участки с началом >= указанного значения
        return queryset.filter(pipes__start_point__gte=value).distinct()

    def filter_end_point(self, queryset, name, value):
        # Фильтруем диагностики, у которых есть участки с концом <= указанного значения
        return queryset.filter(pipes__end_point__lte=value).distinct()
