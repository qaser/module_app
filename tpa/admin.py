from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Factory, Service, ServiceType, Valve, ValveDocument,
                     ValveImage, Work, WorkProof, WorkService)


class FactoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'country',)
    search_fields = ('name', 'country',)
    list_filter = ('country',)


class WorksInServiceInline(admin.TabularInline):
    model = Service.works.through
    min_num = 1


class ValveAdmin(admin.ModelAdmin):
    list_display = (
        'location',
        'title',
        'diameter',
        'pressure',
        'valve_type',
        'factory',
        'year_made',
        'year_exploit',
        'tech_number',
        'factory_number',
        'inventory_number',
        'remote',
        'label',
        'design',
        'drive_type',
        'drive_factory',
        'drive_year_exploit',
        'description',
    )
    search_fields = (
        'location',
        'title',
        'diameter',
        'pressure',
        'valve_type',
        'factory',
        'year_made',
        'year_exploit',
        'tech_number',
        'factory_number',
        'inventory_number',
        'remote',
        'label',
        'design',
        'drive_type',
        'drive_factory',
        'drive_year_exploit',
    )
    list_filter = (
        'title',
        'diameter',
        'pressure',
        'valve_type',
        'factory',
        'remote',
        'design',
        'drive_type',
    )
    empty_value_display = '-'


class ServiceTypeAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('name', 'period', 'valve_type', 'min_diameter', 'max_diameter')
    search_fields = ('name', 'valve_type',)
    list_filter = ('valve_type', 'name')


class WorkAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('description', 'service_type', 'planned')
    search_fields = ('service_type',)
    list_filter = ('service_type', 'planned')


class ServiceAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('service_type', 'valve', 'reg_date', 'prod_date', 'executor',)
    search_fields = ('service_type', 'valve', 'works',)
    list_filter = ('service_type', 'prod_date')
    inlines = (WorksInServiceInline,)


class WorkServiceAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('service', 'work', 'done', 'faults')
    search_fields = ('service', 'work', 'done')
    list_filter = ('service', 'work', 'done',)


class DocumentAdmin(admin.ModelAdmin):
    empty_value_display = '-'


class WorkProofAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('file', 'name', 'work',)


class ImageAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


admin.site.register(Factory, FactoryAdmin)
admin.site.register(Valve, ValveAdmin)
admin.site.register(ValveDocument, DocumentAdmin)
admin.site.register(ValveImage, ImageAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(WorkService, WorkServiceAdmin)
admin.site.register(WorkProof, WorkProofAdmin)
