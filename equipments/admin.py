from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Department, Equipment


class EquipmentInline(admin.TabularInline):
    model = Equipment.departments.through
    extra = 1
    verbose_name = 'Связанное оборудование'
    verbose_name_plural = 'Связанное оборудование'
    raw_id_fields = ('equipment',)  # Для быстрого выбора оборудования


class ChildDepartmentInline(admin.TabularInline):
    model = Department
    fk_name = 'parent'
    extra = 1
    fields = ('name',)  # Только поле name для дочерних подразделений
    verbose_name = 'Дочернее подразделение'
    verbose_name_plural = 'Дочерние подразделения'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(level__lte=1)  # Ограничиваем глубину вложенности


@admin.register(Department)
class DepartmentAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent', 'equipment_count')
    list_filter = ('parent',)
    search_fields = ('name', 'parent__name')
    mptt_level_indent = 20
    inlines = [ChildDepartmentInline, EquipmentInline]
    fields = ('name', 'parent')
    raw_id_fields = ('parent',)  # Для удобного выбора родителя

    def equipment_count(self, obj):
        return obj.equipments.count()
    equipment_count.short_description = 'Кол-во оборудования'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('equipments')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Department):  # Для дочерних подразделений
                if not instance.parent_id:
                    instance.parent = form.instance
            instance.save()
        formset.save_m2m()
