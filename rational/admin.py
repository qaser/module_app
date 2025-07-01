from django.contrib import admin
from django.utils.html import format_html

from .models import (AnnualPlan, Proposal, ProposalDocument, ProposalStatus,
                     QuarterlyPlan)


class QuarterlyPlanInline(admin.TabularInline):
    model = QuarterlyPlan
    extra = 0  # Не добавлять пустые строки
    readonly_fields = ('quarter',)  # Запрещаем изменять квартал вручную

    def get_fields(self, request, obj=None):
        return (
            'quarter',
            'planned_proposals',
            'planned_economy',
        )


@admin.register(AnnualPlan)
class AnnualPlanAdmin(admin.ModelAdmin):
    list_filter = ('year', 'department')  # Фильтрация
    search_fields = ('department__name',)  # Поиск по названию подразделения
    inlines = [QuarterlyPlanInline]  # Встроенный квартальный план
    list_display = (
        'indented_department',
        'year',
        'total_proposals',
        'total_economy',
        'sum_economy',
        'completed_proposals',
    )

    def indented_department(self, obj):
        indent = '...' * obj.department.level  # Генерируем отступы
        return f"{indent} {obj.department.name}"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Сортируем по tree_id и lft для правильного отображения иерархии
        queryset = queryset.order_by('department__tree_id', 'department__lft')
        return queryset


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'reg_num',
        'reg_date',
        'department',
        'get_authors',
        'title',
        'category',
        'is_economy',
    )
    list_filter = (
        'category',
        'is_economy',
        'department',
    )
    search_fields = (
        'reg_num',
        'description',
        'department__name',  # Поиск по названию подразделения
    )
    filter_horizontal = ('authors',)
    autocomplete_fields = ['department']
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


@admin.register(ProposalDocument)
class DocumentAdmin(admin.ModelAdmin):
    empty_value_display = '-'


@admin.register(ProposalStatus)
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
