import django_filters as df
from django.db.models import Q

from equipments.models import Equipment, Department
from module_app.utils import create_choices
from users.models import Role
from .mixins import EquipmentAccessMixin

from .models import Valve


class ValveFilter(df.FilterSet):
    department = df.ModelChoiceFilter(
        queryset=Department.objects.none(),
        method='filter_by_department',
        label='Структурное подразделение',
        required=False
    )
    equipment = df.ModelChoiceFilter(
        queryset=Equipment.objects.none(),
        method='filter_by_equipment',
        label='Место нахождения'
    )
    diameter = df.ChoiceFilter(
        field_name='diameter',
        lookup_expr='exact',
        choices=lambda: Valve.objects.values_list('diameter', 'diameter').distinct()
    )
    pressure = df.ChoiceFilter(
        field_name='pressure',
        lookup_expr='exact',
        choices=lambda: Valve.objects.values_list('pressure', 'pressure').distinct()
    )
    tech_number = df.ChoiceFilter(
        field_name='tech_number',
        lookup_expr='exact',
        choices=lambda: Valve.objects.values_list('tech_number', 'tech_number').distinct()
    )
    design = df.ChoiceFilter(
        field_name='design',
        lookup_expr='exact',
        choices=lambda: Valve.objects.values_list('design', 'design').distinct()
    )


    def __init__(self, *args, **kwargs):
        user = kwargs['request'].user
        super(ValveFilter, self).__init__(*args, **kwargs)
        if user.role != Role.ADMIN:
            self.filters.pop('department', None)
        else:
            # Для ADMIN настраиваем отображение иерархии подразделений
            self.filters['department'].field.queryset = Department.objects.all()
            self.filters['department'].field.label_from_instance = lambda obj: f"{'..' * obj.level} {obj.name}"

        self.base_queryset = Equipment.objects.none()

        if user.role == Role.ADMIN:
            self.base_queryset = Equipment.objects.all()
        elif user.role == Role.MANAGER and user.department:
            root = user.department.get_root()
            departments = root.get_descendants(include_self=True)
            self.base_queryset = Equipment.objects.filter(departments__in=departments)
        elif user.role == Role.EMPLOYEE and user.department:
            departments = user.department.get_descendants(include_self=True)
            self.base_queryset = Equipment.objects.filter(departments__in=departments)

        if 'equipment' in self.filters:
            # Получаем полные пути для всех equipment
            equipment_with_paths = []
            for eq in self.base_queryset.order_by('tree_id', 'lft'):
                path = ' - '.join([anc.name for anc in eq.get_ancestors(include_self=True)])
                equipment_with_paths.append((eq.id, path))

            # Создаем новый queryset и подменяем label_from_instance
            self.filters['equipment'].field.queryset = self.base_queryset
            self.filters['equipment'].field.label_from_instance = lambda obj: next(
                (path for (id_, path) in equipment_with_paths if id_ == obj.id),
                obj.name  # fallback
            )

    def filter_by_equipment(self, queryset, name, value):
        if value and self.base_queryset.exists():
            descendants = value.get_descendants(include_self=True)
            return queryset.filter(
                equipment__in=descendants & self.base_queryset
            )
        return queryset.none()

    def filter_by_department(self, queryset, name, value):
        """Фильтрация по подразделению (только для ADMIN)"""
        if value and self.request.user.role == Role.ADMIN:
            return queryset.filter(equipment__departments=value)
        return queryset

    class Meta:
        model = Valve
        fields = [
            'department',
            'equipment',
            'title',
            'diameter',
            'pressure',
            'valve_type',
            'factory',
            'tech_number',
            'drive_type'
        ]
