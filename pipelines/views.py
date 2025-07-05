from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from equipments.models import Equipment
from users.models import Role
from .models import PipeRepair, Pipeline, PipeState

from django_tables2 import SingleTableMixin
from django_filters.views import FilterView




@login_required
def scheme_pipelines(request):
    # pipeline = Pipeline.objects.all()
    state_choices = PipeState.STATE_CHOICES
    return render(
        request,
        'pipelines/index.html',
        {'state_choices': state_choices}
    )


class PipeRepairsView(SingleTableMixin, FilterView):
    model = PipeRepair
    table_class = PipeRepairTable
    paginate_by = 39
    template_name = 'pipelines/pipelines_repairs.html'
    filterset_class = PipeRepairFilter

    def get_queryset(self):
        user = self.request.user
        queryset = filter_by_user_role(user, Proposal.objects.all())

        # Аннотируем queryset, чтобы добавить корневое оборудование
        queryset = queryset.annotate(
            department_root_name=Subquery(
                Department.objects.filter(
                    tree_id=OuterRef('department__tree_id'),
                    level=0  # Корневой элемент имеет level=0
                ).values('name')[:1]
            )
        )
        return queryset

    def get_table_kwargs(self):
        return {'user': self.request.user}
