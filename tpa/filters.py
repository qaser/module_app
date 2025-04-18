import django_filters as df
from django.db.models import Q

from equipments.models import Equipment
from module_app.utils import create_choices
from users.models import Role

from .models import Valve


class ValveFilter(df.FilterSet):
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

        base_level = 0  # Базовый уровень для отступов

        if user.role == Role.ADMIN:
            self.base_queryset = Equipment.objects.all()
            self.filters['equipment'].field.queryset = Equipment.objects.all()

        elif user.role == Role.MANAGER:
            if user.equipment:
                # Получаем корень ветки, к которой принадлежит пользователь
                root = user.equipment.get_root()
                # Фильтруем все оборудование от корня (вся ветка пользователя)
                self.base_queryset = root.get_descendants(include_self=True)
                # Показываем в фильтре только оборудование с одним родителем, но из своей ветки
                self.filters['equipment'].field.queryset = self.base_queryset.filter(parent__isnull=False)
                base_level = root.level
            else:
                self.filters['equipment'].field.queryset = Equipment.objects.none()
                self.base_queryset = Equipment.objects.none()

        elif user.role == Role.EMPLOYEE:
            if user.equipment:
                descendants = user.equipment.get_descendants(include_self=True)
                self.filters['equipment'].field.queryset = Equipment.objects.filter(id__in=descendants.values('id'))
                self.base_queryset = Equipment.objects.filter(id__in=descendants.values('id'))
                base_level = user.equipment.level
            else:
                self.filters['equipment'].field.queryset = Equipment.objects.none()
                self.base_queryset = Equipment.objects.none()

        # Отображаем иерархию в поле выбора
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

    class Meta:
        model = Valve
        fields = [
            'equipment',
            'title',
            'diameter',
            'pressure',
            'valve_type',
            'factory',
            'tech_number',
            'drive_type'
        ]
