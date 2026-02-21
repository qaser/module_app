from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, F, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from equipments.models import Department
from django.core.exceptions import ValidationError

from .models import (Document, Event, EventCompletion, EventInstance,
                     EventStatus, Order,
                     OrderActivity, OrderActivityResponsibility, Protocol,
                     ProtocolActivity, ProtocolActivityResponsibility)

# @admin.register(Protocol)
# class ProtocolAdmin(admin.ModelAdmin):
#     list_display = ('subject', 'num_protocol', 'date_protocol', 'title')
#     list_filter = ('subject', 'date_protocol', 'is_archive', 'is_complete')


# @admin.register(ProtocolActivity)
# class ProtocolActivityAdmin(admin.ModelAdmin):
#     list_display = (
#         'protocol',
#         'deadline_type',
#         'deadline_date',
#         'status',
#         'actual_completion_date',
#     )
#     list_filter = ('protocol', 'deadline_type', 'status',)


# @admin.register(ProtocolActivityResponsibility)
# class ProtocolActivityResponsibilityAdmin(admin.ModelAdmin):
#     list_display = (
#         'activity',
#         'department',
#         'status',
#         'actual_completion_date',
#         'comment',
#         'updated_at',
#     )
#     list_filter = ('department', 'status',)


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('num_order', 'date_order', 'title')
#     list_filter = ('date_order', 'is_archive', 'is_complete')


# @admin.register(OrderActivity)
# class OrderActivityAdmin(admin.ModelAdmin):
#     list_display = (
#         'order',
#         'deadline_type',
#         'deadline_date',
#         'status',
#         'actual_completion_date',
#     )
#     list_filter = ('order', 'deadline_type', 'status',)


# @admin.register(OrderActivityResponsibility)
# class OrderActivityResponsibilityAdmin(admin.ModelAdmin):
#     list_display = (
#         'activity',
#         'department',
#         'status',
#         'actual_completion_date',
#         'comment',
#         'updated_at',
#     )
#     list_filter = ('department', 'status',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('full_title', 'category', 'date_doc', 'num_doc', 'is_complete', 'is_archived')
    list_filter = ('category', 'is_complete', 'is_archived', 'subject')
    search_fields = ('title', 'num_doc')
    readonly_fields = ('full_title',)
    fieldsets = (
        (None, {
            'fields': ('category', 'title', 'num_doc', 'date_doc', 'subject')
        }),
        ('Статус', {
            'fields': ('is_complete', 'is_archived')
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('description', 'document', 'schedule_type', 'get_period', 'is_archived')
    list_filter = ('schedule_type', 'is_archived', 'document')
    search_fields = ('description',)
    raw_id_fields = ('document',)  # для удобства при большом количестве документов
    fieldsets = (
        (None, {
            'fields': ('document', 'description', 'departments', 'schedule_type')
        }),
        ('Периодическое повторение', {
            'classes': ('collapse',),
            'fields': ('period_unit', 'period_interval'),
            'description': 'Заполняется, если тип — "Периодическое"'
        }),
        # ('Относительное расписание', {
        #     'classes': ('collapse',),
        #     'fields': ('relative_base', 'relative_position', 'relative_day'),
        #     'description': 'Заполняется, если тип — "Относительное"'
        # }),
        ('Фиксированная дата', {
            'classes': ('collapse',),
            'fields': ('due_date',),
            'description': 'Заполняется, если тип — "Фиксированная дата"'
        }),
        ('Архив', {
            'fields': ('is_archived',)
        }),
    )

    def get_period(self, obj):
        if obj.schedule_type == 'periodic' and obj.period_unit and obj.period_interval:
            return f"Каждые {obj.period_interval} {obj.get_period_unit_display()}"
        return "-"
    get_period.short_description = 'Период'

    # def get_relative_rule(self, obj):
    #     if obj.schedule_type == 'relative' and obj.relative_base:
    #         pos = obj.get_relative_position_display() or ''
    #         day = obj.relative_day or 0
    #         base = obj.get_relative_base_display() or ''
    #         return f"{pos} {day} дней от {base.lower()}"
    #     return "-"
    # get_relative_rule.short_description = 'Правило смещения'


@admin.register(EventInstance)
class EventInstanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'due_date', 'status', 'is_archived', 'completed_at')
    list_filter = ('status', 'is_archived', 'due_date', 'event__document')
    list_editable = ('status', 'is_archived')
    readonly_fields = ('event', 'status', 'completed_at')
    search_fields = ('event__description',)
    date_hierarchy = 'due_date'


@admin.register(EventCompletion)
class EventCompletionAdmin(admin.ModelAdmin):
    list_display = ('department', 'instance', 'status', 'actual_completion_date', 'assigned_by', 'updated_at')
    list_filter = ('status', 'department', 'assigned_by', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('instance',)  # удобно при большом числе инстансов
    search_fields = ('department__name', 'comment')
    date_hierarchy = 'updated_at'
