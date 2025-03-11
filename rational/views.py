import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from equipments.models import Equipment
from users.models import ModuleUser, Role

from .filters import ProposalFilter, PlanFilter
from .forms import ProposalForm
from .models import Plan, Proposal
from .tables import ProposalTable, PlanTable


class ProposalView(SingleTableMixin, FilterView):
    model = Proposal
    table_class = ProposalTable
    paginate_by = 39
    template_name = 'rational/index.html'
    filterset_class = ProposalFilter

    def get_queryset(self):
        user = self.request.user
        return filter_proposal_by_user_role(user)

    def get_table_kwargs(self):
       return {'user': self.request.user}


def filter_proposal_by_user_role(user):
    if user.role == Role.ADMIN:
        # ADMIN видит всё оборудование
        return Proposal.objects.all()
    elif user.role == Role.MANAGER:
        # MANAGER видит всё оборудование своей ветки, начиная со второго уровня
        if user.equipment:
            # Получаем корень ветки пользователя
            root = user.equipment.get_root()
            # Получаем всех потомков корня (вся ветка)
            descendants = root.get_descendants(include_self=True)
            # Фильтруем оборудование, начиная со второго уровня
            return Proposal.objects.filter(equipment__in=descendants, equipment__level__gte=1)
        else:
            return Proposal.objects.none()
    elif user.role == Role.EMPLOYEE:
        # EMPLOYEE видит всё оборудование своей ветки, начиная с уровня своего оборудования
        if user.equipment:
            # Получаем всех потомков оборудования пользователя
            descendants = user.equipment.get_descendants(include_self=True)
            return Proposal.objects.filter(equipment__in=descendants)
        else:
            return Proposal.objects.none()
    else:
        return Proposal.objects.none()


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


class PlanView(SingleTableMixin, FilterView):
    model = Plan
    table_class = PlanTable
    paginate_by = 39
    template_name = 'rational/index-plans.html'
    filterset_class = PlanFilter

    def get_queryset(self):
        # Фильтруем планы, оставляя только корневые (parent=None)
        return Plan.objects.filter(parent__isnull=True)
