from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Equipment, TypeOfEquipment


class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 1


@admin.register(Equipment)
class EquipmentAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent', 'type_equipment')  # Поля для отображения в списке
    search_fields = ('name', 'type_equipment')  # Поля для поиска
    list_filter = ('parent', 'type_equipment')  # Фильтры
    mptt_level_indent = 20  # Отступ для отображения иерархии
    inlines = [EquipmentInline]  # Добавляем inline для дочернего оборудования


@admin.register(TypeOfEquipment)
class TypeOfEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Поля для отображения в списке
    search_fields = ('name',)  # Поля для поиска
