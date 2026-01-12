from multiprocessing import Pipe

from django.contrib.auth.decorators import login_required
from django.db.models import CharField, Exists, FloatField, OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from equipments.models import Equipment
from pipelines.filters import (AnomalyFilter, BendFilter, DiagnosticsFilter, RepairFilter, TubeFilter, TubeUnitFilter,
                               TubeVersionFilter)
from pipelines.tables import (AnomalyTable, BendTable, DiagnosticsTable, RepairTable, TubeTable, TubeUnitTable,
                              TubeVersionTable)
from users.models import ModuleUser, Role

from .models import (Anomaly, Bend, ComplexPlan, Diagnostics, Pipe, PipeDepartment, Pipeline,
                     PipeState, Repair, Tube, TubeUnit, TubeVersion)


@login_required
def scheme_pipelines(request):
    state_choices = PipeState.STATE_CHOICES
    return render(
        request,
        'pipelines/index.html',
        {'state_choices': state_choices}
    )


@login_required
def single_pipe(request, pipe_id):
    # pipe = Pipe.objects.filter(id=pipe_id)
    return render(
        request,
        'pipelines/single_pipe.html',
        {'pipe_id': pipe_id}
    )


@login_required
def single_tube(request, tube_id, pipe_id):
    # tube = Tube.objects.filter(id=tube_id)
    return render(
        request,
        'pipelines/single_tube.html',
        {'tube_id': tube_id}
    )


@login_required
def single_node(request):
    return render(
        request,
        'pipelines/single_node.html',
        {}
    )


@login_required
def single_diagnostic(request, diagnostic_id):
    # pipe = Pipe.objects.filter(id=pipe_id)
    return render(
        request,
        'pipelines/single_diagnostic.html',
        {'diagnostic_id': diagnostic_id}
    )


class RepairsView(SingleTableMixin, FilterView):
    model = Repair
    table_class = RepairTable
    paginate_by = 39
    template_name = 'pipelines/pipelines_repairs.html'
    filterset_class = RepairFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == Role.ADMIN:
            return queryset  # ADMIN видит все ремонты

        else:
            if user.department:
                root_department = user.department.get_root()
                departments = root_department.get_descendants(include_self=True)
                pipe_repairs = queryset.filter(
                    pipe__pipedepartment__department__in=departments
                ).distinct()
                node_repairs = queryset.filter(
                    node__equipment__departments__in=departments
                ).distinct()
                return (pipe_repairs | node_repairs).distinct()
            return queryset.none()


class DiagnosticsView(SingleTableMixin, FilterView):
    model = Diagnostics
    table_class = DiagnosticsTable
    paginate_by = 39
    template_name = 'pipelines/pipelines_diagnostics.html'
    filterset_class = DiagnosticsFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # diagnostic_id = self.kwargs['diagnostic_id']

        # Базовая оптимизация запросов
        queryset = queryset.prefetch_related(
            'pipes__pipeline',
            'pipes__pipedepartment_set__department'
        )

        if user.role == Role.ADMIN:
            return queryset

        else:
            if user.department:
                root_department = user.department.get_root()
                departments = root_department.get_descendants(include_self=True)

                return queryset.filter(
                    pipes__pipedepartment__department__in=departments
                ).distinct()
            return queryset.none()

    # def get_context_data(self, **kwargs):
    #     """
    #     Добавляем ID объекта диагностики в контекст.
    #     """
    #     context = super().get_context_data(**kwargs)
    #     context['diagnostic_id'] = self.kwargs['diagnostic_id']
    #     return context


class DiagnosticTubesView(SingleTableMixin, FilterView):
    model = TubeVersion
    table_class = TubeVersionTable
    template_name = 'pipelines/diagnostic_tubes.html'
    filterset_class = TubeVersionFilter
    paginate_by = 50

    def get_queryset(self):
        return (
            TubeVersion.objects
            .filter(diagnostics_id=self.kwargs['diagnostic_id'])
            .order_by('odometr_data')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnostic_id'] = self.kwargs['diagnostic_id']
        return context


class DiagnosticTubeUnitsView(SingleTableMixin, FilterView):
    model = TubeUnit
    table_class = TubeUnitTable
    template_name = 'pipelines/diagnostic_tubeunits.html'
    filterset_class = TubeUnitFilter
    paginate_by = 50

    def get_queryset(self):
        diagnostic_id = self.kwargs['diagnostic_id']
        queryset = TubeUnit.objects.filter(tube__diagnostics_id=diagnostic_id)
        # return queryset.select_related('tube')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnostic_id'] = self.kwargs['diagnostic_id']
        return context


class DiagnosticBendsView(SingleTableMixin, FilterView):
    model = Bend
    table_class = BendTable
    template_name = 'pipelines/diagnostic_bends.html'
    filterset_class = BendFilter
    paginate_by = 50

    def get_queryset(self):
        diagnostic_id = self.kwargs['diagnostic_id']
        queryset = Bend.objects.filter(tube__diagnostics_id=diagnostic_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnostic_id'] = self.kwargs['diagnostic_id']
        return context


class DiagnosticAnomaliesView(SingleTableMixin, FilterView):
    model = Anomaly
    table_class = AnomalyTable
    template_name = 'pipelines/diagnostic_anomalies.html'
    filterset_class = AnomalyFilter
    paginate_by = 50

    def get_queryset(self):
        diagnostic_id = self.kwargs['diagnostic_id']
        queryset = Bend.objects.filter(tube__diagnostics_id=diagnostic_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnostic_id'] = self.kwargs['diagnostic_id']
        return context


class TubesView(SingleTableMixin, FilterView):
    model = Tube
    table_class = TubeTable
    template_name = 'pipelines/pipe_tubes.html'
    filterset_class = TubeFilter
    paginate_by = 50

    def get_queryset(self):
        pipe_id = self.kwargs['pipe_id']
        # Базовый подзапрос последней версии
        last_version_qs = (
            TubeVersion.objects
            .filter(tube=OuterRef('pk'))
            .order_by('-date')
        )
        # Последняя версия с НЕ пустой маркой стали
        last_steel_qs = (
            TubeVersion.objects
            .filter(tube=OuterRef('pk'))
            .exclude(steel_grade__isnull=True)
            .exclude(steel_grade='')
            .order_by('-date')
        )
        # Проверка наличия элементов обустройства у последней версии
        unit_exists_qs = TubeUnit.objects.filter(
            tube=Subquery(last_version_qs.values('id')[:1])
        )
        queryset = (
            Tube.objects
            .filter(pipe_id=pipe_id, active=True)
            .annotate(
                last_version_id=Subquery(
                    last_version_qs.values('id')[:1]
                ),
                last_length=Subquery(
                    last_version_qs.values('tube_length')[:1],
                    output_field=FloatField()
                ),
                last_thickness=Subquery(
                    last_version_qs.values('thickness')[:1],
                    output_field=FloatField()
                ),
                last_diameter=Subquery(
                    last_version_qs.values('diameter')[:1]
                ),
                last_category=Subquery(
                    last_version_qs.values('category')[:1]
                ),
                last_type=Subquery(
                    last_version_qs.values('tube_type')[:1]
                ),
                last_odometr=Subquery(
                    last_version_qs.values('odometr_data')[:1],
                    output_field=FloatField()
                ),
                last_steel_grade=Subquery(
                    last_steel_qs.values('steel_grade')[:1],
                    output_field=CharField()
                ),
                has_units=Exists(unit_exists_qs),
            )
            .order_by('last_odometr', 'tube_num')
        )
        return queryset

    def get_filterset_kwargs(self, filterset_class):
        """
        Передаём отфильтрованный queryset в фильтр.
        """
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['queryset'] = self.get_queryset()
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Добавляем ID участка в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['pipe_id'] = self.kwargs['pipe_id']
        return context
