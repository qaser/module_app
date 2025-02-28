from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Leak, LeakDocument, LeakImage


class LeaksAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = (
        # 'direction',
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
        'is_done',
        'note',
        'is_draft',
    )
    search_fields = (
        # 'direction',
        'place',
        'equipment',
        'specified_location',
        'is_done',
        'detector',
        'executor',
        'detection_date',
        'is_draft',
    )
    list_filter = ('place', 'equipment', 'detection_date', 'is_done', 'is_draft')


class DocumentAdmin(admin.ModelAdmin):
    empty_value_display = '-'


class ImageAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


admin.site.register(Leak, LeaksAdmin)
admin.site.register(LeakDocument, DocumentAdmin)
admin.site.register(LeakImage, ImageAdmin)
