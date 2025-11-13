from multiprocessing import Pipe

from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Q, QuerySet, Subquery, Exists
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from equipments.models import Equipment
from pipelines.filters import DiagnosticsFilter, RepairFilter, TubeFilter
from pipelines.tables import DiagnosticsTable, RepairTable, TubeTable
from users.models import ModuleUser, Role

from .models import (ComplexPlan, Diagnostics, Pipe, PipeDepartment, Pipeline,
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


class TubesView(SingleTableMixin, FilterView):
    model = Tube
    table_class = TubeTable
    template_name = 'pipelines/pipe_tubes.html'
    filterset_class = TubeFilter
    paginate_by = 50

    def get_queryset(self):
        pipe_id = self.kwargs['pipe_id']

        # Субзапрос для последней версии
        latest_version_subquery = TubeVersion.objects.filter(
            tube=OuterRef('pk')
        ).order_by('-date')

        # Субзапрос для проверки наличия элементов обустройства
        unit_exists_subquery = TubeUnit.objects.filter(tube=OuterRef('last_version_id'))

        # Субзапрос для типа элемента обустройства
        unit_type_subquery = TubeUnit.objects.filter(
            tube=OuterRef('last_version_id')
        ).order_by('id').values('unit_type')[:1]

        queryset = (
            Tube.objects.filter(pipe_id=pipe_id, active=True)
            .annotate(
                last_length=Subquery(latest_version_subquery.values('tube_length')[:1]),
                last_thickness=Subquery(latest_version_subquery.values('thickness')[:1]),
                last_diameter=Subquery(latest_version_subquery.values('diameter')[:1]),
                last_category=Subquery(latest_version_subquery.values('category')[:1]),
                last_type=Subquery(latest_version_subquery.values('tube_type')[:1]),
                last_steel_grade=Subquery(latest_version_subquery.values('steel_grade')[:1]),
                last_version_id=Subquery(latest_version_subquery.values('id')[:1]),
                has_units=Exists(unit_exists_subquery),
            )
            .order_by('tube_num')
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



# class PlansView(SingleTableMixin, FilterView):
#     model = ComplexPlan
#     table_class = ComplexPlanTable
#     paginate_by = 39
#     template_name = 'pipelines/pipelines_plans.html'
#     filterset_class = ComplexPlanFilter

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         user = self.request.user

#         if user.role == Role.ADMIN:
#             return queryset  # ADMIN видит все ремонты

#         else:
#             if user.department:
#                 root_department = user.department.get_root()
#                 departments = root_department.get_descendants(include_self=True)
#                 pipe_diagnostics = queryset.filter(
#                     pipe__pipedepartment__department__in=departments
#                 ).distinct()
#                 node_diagnostics = queryset.filter(
#                     node__equipment__departments__in=departments
#                 ).distinct()
#                 return (pipe_diagnostics | node_diagnostics).distinct()
#             return queryset.none()
