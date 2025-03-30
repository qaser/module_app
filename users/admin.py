from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from equipments.models import Department

from .models import ModuleUser, UserAppRoute
from django import forms


def get_form(self, request, obj=None, **kwargs):
    form = super().get_form(request, obj, **kwargs)
    form.base_fields['birth_date'].widget = admin.widgets.AdminDateWidget()
    return form


@admin.register(UserAppRoute)
class UserAppRouteAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'user', 'department')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department':
            kwargs['queryset'] = Department.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ModuleUser)
class ModuleUserAdmin(UserAdmin):
    list_display = ('username', 'get_lastname_initials', 'department', 'email', 'role', 'service_num',)
    search_fields = ('username', 'email', 'last_name', 'first_name', 'department__name', 'service_num')
    list_filter = ('role', 'department',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'job_position',
            'department',
            'service_num',
            'birth_date'
        )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions',)
    autocomplete_fields = ['department']

    @admin.display(description='Фамилия И.О.')
    def get_lastname_initials(self, obj):
        return obj.lastname_and_initials
