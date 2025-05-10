from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Leak, LeakDocument, LeakImage, LeakStatus


@admin.register(Leak)
class LeaksAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = (
        'place',
        'equipment',
        'specified_location',
        'description',
        'type_leak',
        'volume',
        'volume_dinamic',
        'gas_losses',
        'reason',
        'detection_date',
        'planned_date',
        'fact_date',
        'method',
        'detector',
        'executor',
        'plan_work',
        'doc_name',
        'protocol',
        'note',
    )
    search_fields = (
        'place',
        'equipment',
        'specified_location',
        'detector',
        'executor',
        'detection_date',
    )
    list_filter = ('place', 'equipment', 'detection_date',)


@admin.register(LeakDocument)
class DocumentAdmin(admin.ModelAdmin):
    empty_value_display = '-'


@admin.register(LeakImage)
class ImageAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(LeakStatus)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('leak', 'colored_status', 'date_changed', 'owner', 'short_note')
    list_filter = ('status', 'date_changed', 'owner')
    search_fields = ('leak__id', 'owner__username', 'note')
    ordering = ('-date_changed',)
    readonly_fields = ('date_changed',)

    def colored_status(self, obj):
        """ Вывод статуса с цветной подсветкой """
        colors = {
            'reg': 'blue',
            'fixed': 'green',
            'draft': 'gray',
        }
        return format_html(
            '<span style="color: {};">{}</span>', colors.get(obj.status, 'black'), obj.get_status_display()
        )

    colored_status.admin_order_field = 'status'
    colored_status.short_description = 'Статус'

    def short_note(self, obj):
        """ Сокращает длинные примечания для компактного отображения """
        return (obj.note[:50] + '...') if obj.note and len(obj.note) > 50 else obj.note

    short_note.short_description = 'Примечание'
