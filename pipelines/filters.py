import django_filters as df
from django import forms
from django.db.models import Q

from equipments.models import Department
from pipelines.models import (Diagnostics, Node, Pipe, PipeDepartment,
                              Pipeline, Repair, Tube, TubeUnit, TubeVersion)


class TubeFilter(df.FilterSet):
    def get_tube_type_choices():
        qs = (TubeVersion.objects
            .exclude(tube_type__isnull=True)
            .exclude(tube_type__exact='')
            .values_list('tube_type', flat=True)
            .distinct())
        choices = [(val, dict(TubeVersion.TUBE_TYPE).get(val, val)) for val in sorted(qs)]
        return choices

    def get_steel_grade_choices():
        qs = (TubeVersion.objects
            .exclude(steel_grade__isnull=True)
            .exclude(steel_grade__exact='')
            .values_list('steel_grade', flat=True)
            .distinct())
        choices = [(val, val) for val in sorted(qs)]
        return choices

    def get_unit_type_choices():
        # Базовые опции
        base_choices = [
            ('all_units', 'Все элементы обустройства'),
            ('no_units', 'Без элементов обустройства'),
        ]

        # Опции типов элементов обустройства
        unit_choices = [
            (val, label) for val, label in TubeUnit.UNIT_TYPE
        ]

        return base_choices + unit_choices

    tube_num = df.CharFilter(
        label='Номер элемента',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_length = df.ChoiceFilter(
        label='Длина элемента (м)',
        choices=lambda: [
            (val, f"{val} м") for val in sorted(
                set(round(v, 2) for v in TubeVersion.objects.values_list('tube_length', flat=True).distinct() if v)
            )
        ],
        field_name='last_length',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    last_thickness = df.ChoiceFilter(
        label='Толщина стенки (мм)',
        choices=lambda: [
            (val, f"{val} мм") for val in sorted(
                set(round(v, 1) for v in TubeVersion.objects.values_list('thickness', flat=True).distinct() if v)
            )
        ],
        field_name='last_thickness',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    last_type = df.ChoiceFilter(
        label='Тип',
        choices=get_tube_type_choices,
        field_name='last_type',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    last_steel_grade = df.ChoiceFilter(
        label='Марка стали',
        choices=get_steel_grade_choices,
        field_name='last_steel_grade',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    unit_type = df.ChoiceFilter(
        label='Элементы обустройства',
        choices=get_unit_type_choices,
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

    def filter_unit_type(self, queryset, name, value):
        if value == 'all_units':
            # Трубы с любыми элементами обустройства (unit_type не пустой)
            return queryset.exclude(unit_type__isnull=True)
        elif value == 'no_units':
            # Трубы без элементов обустройства (unit_type пустой)
            return queryset.filter(unit_type__isnull=True)
        else:
            # Трубы с конкретным типом элемента обустройства
            return queryset.filter(unit_type=value)


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
