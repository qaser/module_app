import django_filters as df
from django.db.models import OuterRef, Subquery
from django.forms import Select
from django.forms.widgets import Select
from django.utils.functional import lazy

from equipments.models import Department
from users.models import Role

from .models import CATEGORY, AnnualPlan, Proposal, Status


def get_proposal_years():
    return [
        (year, year)
        for year in Proposal.objects.dates('reg_date', 'year')
        .values_list('reg_date__year', flat=True)
        .distinct()
    ]

def get_annual_plan_years():
    return [
        (year, year)
        for year in AnnualPlan.objects.values_list('year', flat=True)
        .distinct().order_by('year')
    ]

class ProposalFilter(df.FilterSet):
    authors = df.CharFilter(
        label='Автор',
        method='filter_by_author',
        lookup_expr='icontains'
    )
    category = df.ChoiceFilter(
        choices=CATEGORY,
        label='Классификатор'
    )
    is_economy = df.BooleanFilter(
        label='Экономический эффект',
        widget=Select(
            choices=[('', '---------'), (True, 'Есть'), (False, 'Нет')]
        )
    )
    department = df.ModelChoiceFilter(
        queryset=Department.objects.none(),
        method='filter_by_department',
        label='Структурное подразделение'
    )
    status = df.ChoiceFilter(
        choices=Status.StatusChoices.choices,
        method='filter_by_status',
        label='Статус'
    )
    year = df.ChoiceFilter(
        choices=lazy(get_proposal_years, list)(),
        label='Год',
        method='filter_by_year'
    )
    quarter = df.ChoiceFilter(
        choices=[
            (1, '1 квартал'),
            (2, '2 квартал'),
            (3, '3 квартал'),
            (4, '4 квартал')
        ],
        label='Квартал',
        method='filter_by_quarter'
    )

    class Meta:
        model = Proposal
        fields = [
            'department',
            'category',
            'is_economy',
            'authors',
            'status',
            'year',
            'quarter'
        ]

    def filter_by_year(self, queryset, name, value):
        if value:
            return queryset.filter(reg_date__year=value)
        return queryset

    def filter_by_quarter(self, queryset, name, value):
        if value:
            value = int(value)
            start_month = 3 * (value - 1) + 1
            end_month = start_month + 2
            return queryset.filter(reg_date__month__gte=start_month, reg_date__month__lte=end_month)
        return queryset

    def filter_by_author(self, queryset, name, value):
        if value:
            return queryset.filter(authors__last_name__icontains=value) | \
                   queryset.filter(authors__first_name__icontains=value) | \
                   queryset.filter(authors__patronymic__icontains=value)
        return queryset

    def filter_by_status(self, queryset, name, value):
        """Фильтрация по последнему статусу"""
        if value == Status.StatusChoices.ACCEPT:
            latest_status = Status.objects.filter(proposal=OuterRef('id')).order_by('-date_changed').values('status')[:1]
            return queryset.annotate(
                latest_status=Subquery(latest_status)
            ).filter(
                latest_status__in=[Status.StatusChoices.ACCEPT, Status.StatusChoices.APPLY]
            )
        else:
            latest_status = Status.objects.filter(proposal=OuterRef('id')).order_by('-date_changed').values('status')[:1]
            return queryset.annotate(
                latest_status=Subquery(latest_status)
            ).filter(
                latest_status=value
            )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('request').user
        super().__init__(*args, **kwargs)
        base_level = 0
        department_queryset = Department.objects.all()
        if user.role == Role.ADMIN:
            self.base_queryset = department_queryset
            self.filters['department'].field.queryset = department_queryset
        elif user.role == Role.MANAGER:
            if user.department:
                root = user.department.get_root()
                self.base_queryset = department_queryset.filter(tree_id=root.tree_id)
                self.filters['department'].field.queryset = self.base_queryset.filter(parent__isnull=False)
                base_level = root.level
            else:
                self.filters['department'].field.queryset = Department.objects.none()
                self.base_queryset = Department.objects.none()
        elif user.role == Role.EMPLOYEE:
            if user.department:
                descendants = user.department.get_descendants(include_self=True)
                self.base_queryset = department_queryset.filter(id__in=descendants.values('id'))
                self.filters['department'].field.queryset = self.base_queryset
                base_level = user.department.level
            else:
                self.filters['department'].field.queryset = Department.objects.none()
                self.base_queryset = Department.objects.none()
        if 'department' in self.filters:
            self.filters['department'].field.queryset = self.filters['department'].field.queryset.order_by('tree_id', 'lft')
            self.filters['department'].field.label_from_instance = lambda obj: f"{'..' * (obj.level - base_level)} {obj.name}"

    def filter_by_department(self, queryset, name, value):
        try:
            if value and self.base_queryset:
                descendants = value.get_descendants(include_self=True)
                queryset = queryset.filter(department__in=descendants & self.base_queryset)
            else:
                queryset = queryset.none()
        except Department.DoesNotExist:
            queryset = queryset.none()
        return queryset


class AnnualPlanFilter(df.FilterSet):
    department = df.ModelChoiceFilter(
        queryset=Department.objects.filter(parent__isnull=True),
        label='Филиалы'
    )
    year = df.ChoiceFilter(
        choices=lazy(get_annual_plan_years, list)(),
        label='Год',
        field_name='year'
    )

    class Meta:
        model = AnnualPlan
        fields = ['department', 'year']
