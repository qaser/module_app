from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ReportParameter, ReportValue


class ReportParameterAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('title', 'period',)
    search_fields = ('title', 'period',)
    list_filter = ('title', 'period',)


class ReportValueAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = (
        'department',
        'reg_date',
        'parameter',
        'author',
        'description',
        'full_num',
        'quarter_num',
        'done_num',
    )
    search_fields = (
        'department',
        'reg_date',
        'parameter',
        'author',
        'description',
        'full_num',
        'quarter_num',
        'done_num',
    )
    list_filter = (
        'department',
        'reg_date',
        'parameter',
        'author',
        'description',
        'full_num',
        'quarter_num',
        'done_num',
    )





admin.site.register(ReportParameter, ReportParameterAdmin)
admin.site.register(ReportValue, ReportValueAdmin)
