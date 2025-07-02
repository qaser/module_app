from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import (ComplexPlan, Defect, Hole, HoleDocument, Node, NodeState,
                     Pipe, PipeDiagrostics, Pipeline, PipeRepair,
                     PipeRepairDocument, PipeRepairStage, PipeState,
                     PlannedWork)


# Фильтры для админки
class StateFilter(admin.SimpleListFilter):
    title = 'Текущее состояние'
    parameter_name = 'current_state'

    def lookups(self, request, model_admin):
        return PipeState.STATE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                states__state_type=self.value(),
                states__end_date__isnull=True
            ).distinct()
        return queryset

# Inline для состояний трубы
class PipeStateInline(admin.TabularInline):
    model = PipeState
    extra = 0
    readonly_fields = ('created_by', 'start_date')
    fields = ('state_type', 'start_date', 'end_date', 'description',
              'current_pressure', 'created_by')

# Inline для участков трубопровода
class PipeInline(admin.TabularInline):
    model = Pipe
    extra = 0
    show_change_link = True
    fields = ('department', 'diameter', 'start_point', 'end_point', 'current_state_display')
    readonly_fields = ('current_state_display',)

    def current_state_display(self, obj):
        state = obj.current_state
        if state:
            color = state.color
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                state.get_state_type_display()
            )
        return "-"
    current_state_display.short_description = "Текущее состояние"

# Inline для узлов
class NodeInline(admin.TabularInline):
    model = Node
    extra = 0
    show_change_link = True
    fields = ('node_type', 'equipment', 'location_point', 'valves_count')
    readonly_fields = ('valves_count',)

    def valves_count(self, obj):
        return obj.equipment.valves.count()
    valves_count.short_description = "Кол-во арматуры"


# Inline для состояний арматуры
class NodeStateInline(admin.TabularInline):
    model = NodeState
    extra = 0
    readonly_fields = ('timestamp', 'changed_by')
    fields = ('state', 'timestamp', 'changed_by', 'comment')


class PipeRepairStageInline(admin.TabularInline):
    model = PipeRepairStage
    extra = 0


class PipeRepairDocumentInline(admin.TabularInline):
    model = PipeRepairDocument
    extra = 0


class DefectInline(admin.TabularInline):
    model = Defect
    extra = 0


class HoleDocumentInline(admin.TabularInline):
    model = HoleDocument
    extra = 0


# Админка для Pipeline
@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'pipes_count', 'nodes_count')
    list_editable = ('order',)
    search_fields = ('title', 'description')
    inlines = [PipeInline, NodeInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            pipes_count=Count('pipes'),
            nodes_count=Count('nodes')
        )

    def pipes_count(self, obj):
        return obj.pipes_count
    pipes_count.short_description = "Участков"

    def nodes_count(self, obj):
        return obj.nodes_count
    nodes_count.short_description = "Узлов"

# Админка для Pipe
@admin.register(Pipe)
class PipeAdmin(admin.ModelAdmin):
    list_display = (
        'pipeline', 'department', 'diameter',
        'start_point', 'end_point', 'current_state_display'
    )
    list_filter = ('pipeline', 'department', StateFilter)
    search_fields = ('pipeline__title', 'department__name')
    inlines = [PipeStateInline]

    def current_state_display(self, obj):
        state = obj.current_state
        if state:
            color = state.color
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                state.get_state_type_display()
            )
        return "-"
    current_state_display.short_description = "Текущее состояние"

# Админка для PipeState
@admin.register(PipeState)
class PipeStateAdmin(admin.ModelAdmin):
    list_display = (
        'pipe', 'state_type_colored', 'start_date',
        'end_date', 'created_by', 'current_pressure'
    )
    list_filter = ('state_type', 'pipe__pipeline', 'pipe__department')
    search_fields = ('pipe__pipeline__title', 'description')
    readonly_fields = ('created_by', 'start_date')

    def state_type_colored(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            obj.color,
            obj.get_state_type_display()
        )
    state_type_colored.short_description = "Состояние"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Админка для Node
@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = (
        'pipeline', 'node_type', 'equipment',
        'location_point', 'valves_count'
    )
    list_filter = ('pipeline', 'node_type')
    search_fields = ('pipeline__title', 'equipment__name')
    # inlines = [NodeStateInline]

    def valves_count(self, obj):
        return obj.equipment.valves.count()
    valves_count.short_description = "ТПА"

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            valves_count=Count('equipment__valves')
        )

# Админка для NodeState
@admin.register(NodeState)
class NodeStateAdmin(admin.ModelAdmin):
    list_display = (
        'node', 'state_display', 'timestamp',
        'changed_by', 'comment_short'
    )
    list_filter = ('state', 'node__node_type')
    search_fields = ('node__node_type',)
    readonly_fields = ('timestamp', 'changed_by')

    def state_display(self, obj):
        color = '#00FF00' if obj.state == 'open' else '#FF0000'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_state_display()
        )
    state_display.short_description = "Состояние"

    def comment_short(self, obj):
        return obj.comment[:50] + '...' if obj.comment else ''
    comment_short.short_description = "Комментарий"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.changed_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PipeRepair)
class PipeRepairAdmin(admin.ModelAdmin):
    list_display = ('pipe', 'start_date', 'end_date', 'description')
    list_filter = ('pipe__pipeline', 'pipe__department')
    search_fields = ('pipe__pipeline__title', 'description')
    inlines = [PipeRepairStageInline, PipeRepairDocumentInline]


@admin.register(PipeDiagrostics)
class PipeDiagrosticsAdmin(admin.ModelAdmin):
    list_display = ('pipe', 'event_date', 'description')
    list_filter = ('pipe__pipeline',)
    search_fields = ('pipe__pipeline__title',)
    inlines = [DefectInline]


@admin.register(Hole)
class HoleAdmin(admin.ModelAdmin):
    list_display = ('pipe', 'location_point', 'cutting_date', 'welding_date')
    list_filter = ('pipe__pipeline',)
    search_fields = ('pipe__pipeline__title',)
    inlines = [HoleDocumentInline]


@admin.register(ComplexPlan)
class ComplexPlanAdmin(admin.ModelAdmin):
    list_display = ('department', 'year')
    list_filter = ('year', 'department')
    search_fields = ('department__name',)


@admin.register(PlannedWork)
class PlannedWorkAdmin(admin.ModelAdmin):
    list_display = ('complex_plan', 'work_type', 'start_date', 'end_date', 'target_object')
    list_filter = ('work_type', 'complex_plan__year')
    search_fields = ('description', 'complex_plan__department__name')

    def target_object(self, obj):
        return obj.pipe or obj.node
    target_object.short_description = 'Объект'
