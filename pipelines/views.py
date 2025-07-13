from multiprocessing import Pipe

from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Q, QuerySet, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from equipments.models import Equipment
from pipelines.filters import DiagnosticsFilter, RepairFilter, TubeFilter
from pipelines.tables import DiagnosticsTable, RepairTable, TubeTable
from users.models import ModuleUser, Role

from .models import (ComplexPlan, Diagnostics, Pipe, PipeDepartment, Pipeline,
                     PipeState, Repair, Tube)


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
    pipe = Pipe.objects.filter(id=pipe_id)
    return render(
        request,
        'pipelines/single_pipe.html',
        {'pipe_id': pipe_id, 'valve': pipe.model._meta.fields}
    )


@login_required
def single_node(request):
    return render(
        request,
        'pipelines/single_node.html',
        {}
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

        if user.role == Role.ADMIN:
            return queryset  # ADMIN видит все ремонты

        else:
            if user.department:
                root_department = user.department.get_root()
                departments = root_department.get_descendants(include_self=True)
                pipe_diagnostics = queryset.filter(
                    pipe__pipedepartment__department__in=departments
                ).distinct()
                node_diagnostics = queryset.filter(
                    node__equipment__departments__in=departments
                ).distinct()
                return (pipe_diagnostics | node_diagnostics).distinct()
            return queryset.none()


class TubesView(SingleTableMixin, FilterView):
    model = Tube
    table_class = TubeTable
    template_name = 'pipelines/pipe_tubes.html'
    filterset_class = TubeFilter
    paginate_by = 50

    def get_queryset(self):
        pipe_id = self.kwargs['pipe_id']
        return Tube.objects.filter(pipe_id=pipe_id)

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['queryset'] = self.get_queryset()
        return kwargs

    def get_context_data(self, **kwargs):
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
