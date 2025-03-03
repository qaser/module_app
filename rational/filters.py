import django_filters as df
from django.db.models import OuterRef, Q, Subquery
from django.forms.widgets import Select

from equipments.models import Equipment
from users.models import Role

from .models import CATEGORY, Proposal, Status


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
    equipment = df.ModelChoiceFilter(
        queryset=Equipment.objects.none(),
        method='filter_by_equipment',
        label='Структурное подразделение'
    )
    status = df.ChoiceFilter(
        choices=Status.StatusChoices.choices,
        method='filter_by_status',
        label='Статус'
    )

    class Meta:
        model = Proposal
        fields = ['equipment', 'category', 'is_economy', 'authors', 'status']

    def filter_by_author(self, queryset, name, value):
        if value:
            return queryset.filter(authors__last_name__icontains=value) | \
                   queryset.filter(authors__first_name__icontains=value) | \
                   queryset.filter(authors__patronymic__icontains=value)
        return queryset

    def filter_by_status(self, queryset, name, value):
        """Фильтрация по последнему статусу"""
        if value == Status.StatusChoices.ACCEPT:
            # Если выбран статус ACCEPT, включаем также APPLY
            latest_status = Status.objects.filter(proposal=OuterRef('id')).order_by('-date_changed').values('status')[:1]
            return queryset.annotate(
                latest_status=Subquery(latest_status)
            ).filter(
                latest_status__in=[Status.StatusChoices.ACCEPT, Status.StatusChoices.APPLY]
            )
        else:
            # Для других статусов фильтруем как обычно
            latest_status = Status.objects.filter(proposal=OuterRef('id')).order_by('-date_changed').values('status')[:1]
            return queryset.annotate(
                latest_status=Subquery(latest_status)
            ).filter(
                latest_status=value
            )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('request').user
        super().__init__(*args, **kwargs)
        base_level = 0  # Базовый уровень отступов

        # Базовый QuerySet без 'Материальной структуры'
        equipment_queryset = Equipment.objects.exclude(structure="Материальная структура")

        if user.role == Role.ADMIN:
            self.base_queryset = equipment_queryset
            self.filters['equipment'].field.queryset = equipment_queryset
        elif user.role == Role.MANAGER:
            if user.equipment:
                root = user.equipment.get_root()
                self.base_queryset = equipment_queryset.filter(tree_id=root.tree_id)
                self.filters['equipment'].field.queryset = self.base_queryset.filter(parent__isnull=False)
                base_level = root.level
            else:
                self.filters['equipment'].field.queryset = Equipment.objects.none()
                self.base_queryset = Equipment.objects.none()
        elif user.role == Role.EMPLOYEE:
            if user.equipment:
                descendants = user.equipment.get_descendants(include_self=True)
                self.base_queryset = equipment_queryset.filter(id__in=descendants.values('id'))
                self.filters['equipment'].field.queryset = self.base_queryset
                base_level = user.equipment.level
            else:
                self.filters['equipment'].field.queryset = Equipment.objects.none()
                self.base_queryset = Equipment.objects.none()

        # Убираем "Материальную структуру" и применяем иерархический отступ
        if 'equipment' in self.filters:
            self.filters['equipment'].field.queryset = self.filters['equipment'].field.queryset.order_by('tree_id', 'lft')
            self.filters['equipment'].field.label_from_instance = lambda obj: f"{'..' * (obj.level - base_level)} {obj.name}"

    def filter_by_equipment(self, queryset, name, value):
        try:
            if value and self.base_queryset:
                descendants = value.get_descendants(include_self=True)
                queryset = queryset.filter(equipment__in=descendants & self.base_queryset)
            else:
                queryset = queryset.none()
        except Equipment.DoesNotExist:
            queryset = queryset.none()
        return queryset
