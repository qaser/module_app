from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ModuleUser


@admin.register(ModuleUser)
class ModuleUserAdmin(UserAdmin):
    # list_display = ('username', 'email', 'lastname_and_initials', 'role', 'structure')  # Поля для отображения в списке
    list_display = ('username', 'email', 'role', 'equipment')  # Поля для отображения в списке
    search_fields = ('username', 'email', 'last_name', 'first_name', 'equipment__name')  # Поля для поиска
    list_filter = ('role', 'equipment')  # Фильтры
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic', 'email', 'job_position', 'equipment')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions',)  # Горизонтальные фильтры для групп и прав
    autocomplete_fields = ['equipment']  # Включаем автодополнение для поля structure
