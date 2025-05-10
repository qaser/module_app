from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Department, Equipment, Pipeline

# Pipeline Admin
@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)

# Department Admin
@admin.register(Department)
class DepartmentAdmin(DraggableMPTTAdmin):
    list_display = ('indented_title', 'parent')
    search_fields = ('name', 'parent__name')  # Поиск по имени и родителю
    list_filter = ('parent',)
    fields = ('name', 'parent')
    autocomplete_fields = ['parent']

    def add_child_department(self, request, queryset):
        for department in queryset:
            Department.objects.create(
                name=f"Новое подразделение {department.name}",
                parent=department
            )
        self.message_user(request, "Дочерние подразделения успешно созданы")
    add_child_department.short_description = "Создать дочернее подразделение"

# Equipment Admin
@admin.register(Equipment)
class EquipmentAdmin(DraggableMPTTAdmin):
    list_display = ('indented_title', 'pipeline')
    fields = ('name', 'parent', 'pipeline', 'departments')
    filter_horizontal = ('departments',)
    list_filter = ('pipeline', 'departments')
    search_fields = ('name',)
    actions = ['add_child_equipment']

    def add_child_equipment(self, request, queryset):
        for equipment in queryset:
            Equipment.objects.create(
                name=f"Новое оборудование {equipment.name}",
                parent=equipment,
                pipeline=equipment.pipeline
            )
        self.message_user(request, "Дочернее оборудование успешно создано")
    add_child_equipment.short_description = "Создать дочернее оборудование"
