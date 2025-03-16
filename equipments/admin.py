from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Department, Equipment


class EquipmentInline(admin.TabularInline):
    model = Equipment.departments.through
    extra = 1


@admin.register(Department)
class DepartmentAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent')  # Поля, отображаемые в списке
    list_filter = ('parent',)  # Фильтр по родительскому объекту
    search_fields = ('name',)  # Поиск по названию
    mptt_level_indent = 20  # Отступ для отображения иерархии
    inlines = [EquipmentInline]


@admin.register(Equipment)
class EquipmentAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent', 'display_departments')  # Поля в списке
    list_filter = ('parent', 'departments')  # Фильтры
    search_fields = ('name',)  # Поиск по названию
    filter_horizontal = ('departments',)  # Удобный выбор подразделений
    mptt_level_indent = 20  # Отступ для отображения иерархии

    def display_departments(self, obj):
        return ", ".join([department.name for department in obj.departments.all()])
    display_departments.short_description = 'Подразделения'
