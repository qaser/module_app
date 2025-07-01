from django.core.cache import cache
from django.db.models import Q

from equipments.models import Department, Equipment
from users.models import Role


class EquipmentAccessMixin:
    """Миксин для контроля доступа к оборудованию"""

    CACHE_TIMEOUT = 60 * 15  # 15 минут кеширования

    def get_accessible_equipment(self, user):
        """Возвращает queryset доступного оборудования с иерархией"""
        cache_key = f'accessible_equipment_{user.id}_{user.role}'
        cached = cache.get(cache_key)

        if cached:
            return Equipment.objects.filter(pk__in=cached)

        if user.role == Role.ADMIN:
            qs = Equipment.objects.all()
        elif user.role in [Role.MANAGER, Role.EMPLOYEE] and user.department:
            departments = user.department.get_root().get_descendants(include_self=True)
            qs = Equipment.objects.filter(departments__in=departments)
        else:
            qs = Equipment.objects.none()

        cache.set(cache_key, list(qs.values_list('pk', flat=True)), self.CACHE_TIMEOUT)
        return qs

    def get_equipment_hierarchy_labels(self, queryset):
        """Генерирует метки с иерархией для выпадающего списка"""
        return [
            (eq.id, ' - '.join(anc.name for anc in eq.get_ancestors(include_self=True)))
            for eq in queryset.order_by('tree_id', 'lft')
        ]

    def setup_department_filter(self, user):
        """Настраивает фильтр подразделений для ADMIN"""
        if hasattr(self, 'filters') and 'department' in self.filters:
            if user.role != Role.ADMIN:
                self.filters.pop('department')
            else:
                self.filters['department'].field.queryset = Department.objects.all()
                self.filters['department'].field.label_from_instance = (
                    lambda obj: f"{'..' * obj.level} {obj.name}"
                )
