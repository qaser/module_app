import django_filters as df
from django import forms
from django.db.models import Q

from equipments.models import Department
from pipelines.models import (Diagnostics, Node, Pipe, PipeDepartment, Pipeline,
                              Repair, Tube)


class TubeFilter(df.FilterSet):
    tube_num = df.CharFilter(
        label='Номер трубы',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tube_length = df.ChoiceFilter(
        label='Длина трубы (м)',
        choices=lambda: [(val, f"{val} м") for val in sorted(set(round(tube_length, 2) for tube_length in Tube.objects.values_list('tube_length', flat=True)))],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    thickness = df.ChoiceFilter(
        label='Толщина (мм)',
        choices=lambda: [(val, f"{val} мм") for val in sorted(set(round(thickness, 1) for thickness in Tube.objects.values_list('thickness', flat=True)))],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tube_type = df.ChoiceFilter(
        label='Тип трубы',
        choices=lambda: [(val, val) for val in sorted(set(Tube.objects.values_list('tube_type', flat=True)))],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Tube
        fields = ['tube_num', 'tube_length', 'thickness', 'tube_type']


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

    class Meta:
        model = Diagnostics
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
