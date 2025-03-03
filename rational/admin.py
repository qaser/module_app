from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html

from .models import Plan, Proposal, ProposalDocument, Status


class PlanInline(admin.TabularInline):
    model = Plan
    extra = 4


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'reg_num',
        'reg_date',
        'equipment',
        'get_authors',
        'title',
        'category',
        'is_economy',
        # 'latest_status',
    )
    list_filter = (
        'category',
        'is_economy',
        'equipment',
    )
    search_fields = (
        'reg_num',
        'description',
        'equipment__name',  # Поиск по названию оборудования
    )
    filter_horizontal = ('authors',)
    autocomplete_fields = ['equipment']
    list_editable = ('is_economy',)
    list_per_page = 20

    def get_authors(self, obj):
        return ', '.join([author.get_full_name() for author in obj.authors.all()])

    def get_latest_status(self, obj):
        """Возвращает последний статус заявки"""
        latest_status = obj.statuses.order_by('-date_changed').first()
        return latest_status.get_status_display() if latest_status else "Нет статуса"

    get_latest_status.short_description = 'Статус'
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


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'colored_status', 'date_changed', 'owner', 'short_note')
    list_filter = ('status', 'date_changed', 'owner')
    search_fields = ('proposal__id', 'owner__username', 'note')
    ordering = ('-date_changed',)
    readonly_fields = ('date_changed',)

    def colored_status(self, obj):
        """ Вывод статуса с цветной подсветкой """
        colors = {
            'reg': 'blue',
            'recheck': 'orange',
            'rework': 'red',
            'accept': 'green',
            'reject': 'gray',
            'apply': 'purple',
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
