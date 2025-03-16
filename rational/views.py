import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, QuerySet, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from equipments.models import Department
from users.models import ModuleUser, Role

from .filters import AnnualPlanFilter, ProposalFilter
from .forms import ProposalForm
from .models import AnnualPlan, Proposal
from .tables import AnnualPlanTable, ProposalTable


class ProposalView(SingleTableMixin, FilterView):
    model = Proposal
    table_class = ProposalTable
    paginate_by = 39
    template_name = 'rational/index.html'
    filterset_class = ProposalFilter

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


def filter_by_user_role(user: ModuleUser, queryset: QuerySet, department_field: str = 'department') -> QuerySet:
    """
    Фильтрует queryset в зависимости от роли пользователя.
    :param user: Пользователь (ModuleUser).
    :param queryset: Исходный queryset.
    :param department_field: Название поля, связанного с department (по умолчанию 'department').
    :return: Отфильтрованный queryset.
    """
    if user.role == Role.ADMIN:
        # ADMIN видит всё
        return queryset
    elif user.role == Role.MANAGER:
        # MANAGER видит всё оборудование своей ветки, начиная со второго уровня
        if user.department:
            root = user.department.get_root()
            descendants = root.get_descendants(include_self=True)
            return queryset.filter(**{f"{department_field}__in": descendants, f"{department_field}__level__gte": 0})
        else:
            return queryset.none()
    elif user.role == Role.EMPLOYEE:
        # EMPLOYEE видит всё оборудование своей ветки, начиная с уровня своего оборудования
        if user.department:
            descendants = user.department.get_descendants(include_self=True)
            return queryset.filter(**{f"{department_field}__in": descendants})
        else:
            return queryset.none()
    else:
        return queryset.none()


@login_required
def single_proposal(request, proposal_id):
    proposal = Proposal.objects.filter(id=proposal_id)
    return render(
        request,
        'rational/single-proposal.html',
        {'proposal_id': proposal_id, 'proposal': proposal}
    )


@login_required
def proposal_new(request):
    if request.method == 'POST':
        form = ProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            economy_size = form.cleaned_data.get('economy_size', 0)
            proposal.is_economy = economy_size != 0
            proposal.save()
            authors = form.cleaned_data.get('authors', [])
            proposal.authors.set(authors)

            return redirect('rational:single_proposal', proposal.id)
        else:
            # Если форма не прошла валидацию, выводим ошибки
            print("Форма не прошла валидацию. Ошибки:", form.errors)
    else:
        form = ProposalForm(user=request.user)
    return render(request, 'rational/new-proposal.html', {'form': form})


class AnnualPlanView(SingleTableMixin, FilterView):
    model = AnnualPlan
    table_class = AnnualPlanTable
    paginate_by = 39
    template_name = 'rational/index-plans.html'
    filterset_class = AnnualPlanFilter

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(department__parent__isnull=True)  # Только корневые department
        return filter_by_user_role(user, queryset)


@login_required
def single_plan(request, plan_id):
    plan = get_object_or_404(AnnualPlan, id=plan_id)
    return render(request, 'rational/single-plan.html', {'plan': plan})
