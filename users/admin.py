from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from equipments.models import Department

from .models import ModuleUser, NotificationAppRoute


@admin.register(NotificationAppRoute)
class NotificationAppRouteAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'user', 'department')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department':
            kwargs['queryset'] = Department.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ModuleUser)
class ModuleUserAdmin(UserAdmin):
    # list_display = ('username', 'email', 'lastname_and_initials', 'role', 'structure')  # Поля для отображения в списке
    list_display = ('username', 'email', 'role', 'department')  # Поля для отображения в списке
    search_fields = ('username', 'email', 'last_name', 'first_name', 'department__name')  # Поля для поиска
    list_filter = ('role', 'department')  # Фильтры
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic', 'email', 'job_position', 'department')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions',)  # Горизонтальные фильтры для групп и прав
    autocomplete_fields = ['department']  # Включаем автодополнение для поля structure
