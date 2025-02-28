from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Plan, Proposal, ProposalDocument


class PlanInline(admin.TabularInline):
    model = Plan
    extra = 4


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'reg_num',
        'reg_date',
        'accept_date',
        'equipment',
        'get_authors',
        'title',
        'category',
        'is_economy',
        'is_apply',
    )
    list_filter = (
        'reg_date',
        'accept_date',
        'category',
        'is_economy',
        'is_apply',
        'equipment',
    )
    search_fields = (
        'reg_num',
        'description',
        'equipment__name',  # Поиск по названию оборудования
    )
    filter_horizontal = ('authors',)
    autocomplete_fields = ['equipment']
    list_editable = ('is_economy', 'is_apply')
    list_per_page = 20

    def get_authors(self, obj):
        return ', '.join([author.get_full_name() for author in obj.authors.all()])

    get_authors.short_description = 'Авторы'


@admin.register(Plan)
class PlanAdmin(DraggableMPTTAdmin):
    list_display = (
        'indented_title',
        'year',
        'quarter',
        'equipment',
        'target',
        'completed'
    )
    list_display_links = ('indented_title',)
    list_filter = ('year', 'quarter', 'equipment')
    search_fields = ('equipment__name',)
    ordering = ('tree_id', 'lft')  # ВАЖНО: сортируем по MPTT полям
    mptt_level_indent = 20  # Отступы в дереве
    inlines = [PlanInline]  # Добавляем inline для дочернего оборудования


@admin.register(ProposalDocument)
class DocumentAdmin(admin.ModelAdmin):
    empty_value_display = '-'
