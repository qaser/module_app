from django.contrib import admin

from .models import (Factory, Service, ServiceType, Valve, ValveDocument,
                     ValveImage, Work, WorkProof, WorkService)


@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'country',)
    search_fields = ('name', 'country',)
    list_filter = ('country',)


class WorksInServiceInline(admin.TabularInline):
    model = Service.works.through
    min_num = 1


@admin.register(Valve)
class ValveAdmin(admin.ModelAdmin):
    list_display = (
        'equipment',
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
        'note',
        'is_pipelines_major'
    )
    search_fields = (
        'equipment',
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
        'is_pipelines_major'
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
        'is_pipelines_major'
    )
    empty_value_display = '-'


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('name', 'period', 'valve_type', 'min_diameter', 'max_diameter')
    search_fields = ('name', 'valve_type',)
    list_filter = ('valve_type', 'name')


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('description', 'service_type', 'planned')
    search_fields = ('service_type',)
    list_filter = ('service_type', 'planned')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('service_type', 'valve', 'reg_date', 'prod_date', 'executor',)
    search_fields = ('service_type', 'valve', 'works',)
    list_filter = ('service_type', 'prod_date')
    inlines = (WorksInServiceInline,)


@admin.register(WorkService)
class WorkServiceAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('service', 'work', 'done', 'faults')
    search_fields = ('service', 'work', 'done')
    list_filter = ('service', 'work', 'done',)


@admin.register(ValveDocument)
class DocumentAdmin(admin.ModelAdmin):
    empty_value_display = '-'


@admin.register(WorkProof)
class WorkProofAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = ('file', 'name', 'work',)


@admin.register(ValveImage)
class ImageAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
