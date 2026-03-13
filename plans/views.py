import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import CharField, Exists, FloatField, OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.utils import timezone

from equipments.models import Department
from rational.models import AnnualPlan
from users.models import ModuleUser, Role, UserAppRoute

from .filters import DocumentFilter, EventInstanceFilter
from .models import Document, Event, EventInstance, EventStatus
from .tables import DocumentTable


@login_required
def index(request):
    if not request.user or not request.user.department:
        return None
    root_dept = request.user.department.get_root()
    current_year = timezone.now().year
    annual_plans = AnnualPlan.objects.filter(
        department=root_dept,
        year=current_year
    )
    return render(
        request,
        'plans/index.html',
        {
            'rational_plan': annual_plans.first()
        }
    )


class ReportsView(SingleTableMixin, FilterView):
    model = Document
    table_class = DocumentTable
    paginate_by = 39
    template_name = 'plans/reports.html'
    filterset_class = DocumentFilter

    def get_queryset(self):
        return Document.objects.filter(
            is_archived=False,
            category='report',
        ).order_by('-date_doc', 'num_doc')


class ProtocolsView(SingleTableMixin, FilterView):
    model = Document
    table_class = DocumentTable
    paginate_by = 39
    template_name = 'plans/protocols.html'
    filterset_class = DocumentFilter

    def get_queryset(self):
        return Document.objects.filter(
            is_archived=False,
            category='protocol',
        ).order_by('-date_doc', 'num_doc')


class OrdersView(SingleTableMixin, FilterView):
    model = Document
    table_class = DocumentTable
    paginate_by = 39
    template_name = 'plans/orders.html'
    filterset_class = DocumentFilter

    def get_queryset(self):
        return Document.objects.filter(
            is_archived=False,
            category='order',
        ).order_by('-date_doc', 'num_doc')


class InspectsView(SingleTableMixin, FilterView):
    model = Document
    table_class = DocumentTable
    paginate_by = 39
    template_name = 'plans/inspects.html'
    filterset_class = DocumentFilter

    def get_queryset(self):
        return Document.objects.filter(
            is_archived=False,
            category='inspect',
        ).order_by('-date_doc', 'num_doc')


@login_required
def single_document(request, doc_id, doc_type):
    user = request.user
    doc = get_object_or_404(
        Document,
        id=doc_id,
        category=doc_type
    )

    # Базовый queryset
    events_queryset = EventInstance.objects.filter(
        event__document=doc
    ).select_related(
        'event', 'event__document', 'event__owner'
    ).prefetch_related(
        'completions',
        'completions__department',
        'event__departments',
    ).order_by('due_date')

    # Применяем фильтры
    event_filter = EventInstanceFilter(
        request.GET,
        queryset=events_queryset
    )

    events = event_filter.qs

    # --- Права управления ---
    can_manage_events = False
    if user.department:
        app_routes = UserAppRoute.objects.filter(
            app_name='plans',
            department__in=user.department.get_descendants(include_self=True)
        )
        can_manage_events = (
            user.role == 'admin' or
            app_routes.filter(user=user).exists() or
            app_routes.filter(department=user.department).exists()
        )

    events_with_actions = []
    for instance in events:
        event = instance.event
        departments = event.departments.all()
        # --- выполнение пользователя ---
        user_completion = None
        if user.department:
            user_completion = instance.completions.filter(
                department=user.department
            ).first()
        # --- права действий ---
        can_mark = (
            user.department and
            user.department in departments and
            instance.status != EventStatus.COMPLETED and
            (
                not user_completion or
                user_completion.status != EventStatus.COMPLETED
            )
        )
        can_archive = (
            can_manage_events and
            not event.is_archived
        )
        can_unarchive = (
            can_manage_events and
            event.is_archived
        )
        can_complete = (
            can_manage_events and
            not event.is_archived and
            instance.status != EventStatus.COMPLETED
        )
        # --- подразделения ---
        completions_map = {
            c.department_id: c for c in instance.completions.all()
        }
        departments_info = [
            {
                'department': dept,
                'completion': completions_map.get(dept.id),
                'is_user_department': dept == user.department,
            }
            for dept in departments
        ]
        events_with_actions.append({
            'instance': instance,
            'event': event,
            # computed
            'computed_status': instance.computed_status,
            'days_until_due': instance.days_until_due,
            # permissions
            'user_completion': user_completion,
            'can_mark': can_mark,
            'can_archive': can_archive,
            'can_unarchive': can_unarchive,
            'can_complete': can_complete,
            # data
            'departments_info': departments_info,
        })

    if user.department:
        root = user.department.get_root()
        root_departments = root.get_descendants(include_self=True).order_by('name')
    else:
        root_departments = Department.objects.none()

    statuses = [
        ("completed", 'Выполнено'),
        ("in_work", 'В работе'),
    ]

    template_map = {
        'report': 'plans/single-report.html',
        'protocol': 'plans/single-protocol.html',
        'order': 'plans/single-order.html',
        'inspect': 'plans/single-inspect.html',
    }

    doc_type_display = dict(Document.CATEGORY_CHOICES).get(doc_type, doc_type)

    return render(
        request,
        template_map.get(doc_type, 'plans/single-document.html'),
        {
            'doc': doc,
            'doc_type': doc_type,
            'events_with_actions': events_with_actions,
            'can_manage_events': can_manage_events,
            'EventStatus': EventStatus,
            'user': user,
            'schedule_types': Event.SCHEDULE_TYPE_CHOICES,
            'period_units': Event.PERIOD_UNIT_CHOICES,
            'departments': root_departments,
            'statuses': statuses,
            'filter': event_filter,  # Передаем фильтр в шаблон
        }
    )


@login_required
def document_events(request, doc_type):
    """Все мероприятия определенного типа документов (все отчеты/протоколы/приказы)"""
    user = request.user

    # Получаем ВСЕ документы указанного типа
    docs = Document.objects.filter(category=doc_type)

    # Базовый queryset для ВСЕХ мероприятий всех документов этого типа
    events_queryset = EventInstance.objects.filter(
        event__document__category=doc_type  # Фильтр по типу документа
    ).select_related(
        'event', 'event__document', 'event__owner'
    ).prefetch_related(
        'completions',
        'completions__department',
        'event__departments',
    ).order_by('due_date')

    # Применяем фильтры
    event_filter = EventInstanceFilter(
        request.GET,
        queryset=events_queryset
    )

    events = event_filter.qs

    # --- Права управления ---
    can_manage_events = False
    if user.department:
        app_routes = UserAppRoute.objects.filter(
            app_name='plans',
            department__in=user.department.get_descendants(include_self=True)
        )
        can_manage_events = (
            user.role == 'admin' or
            app_routes.filter(user=user).exists() or
            app_routes.filter(department=user.department).exists()
        )

    events_with_actions = []
    for instance in events:
        event = instance.event
        departments = event.departments.all()
        # --- выполнение пользователя ---
        user_completion = None
        if user.department:
            user_completion = instance.completions.filter(
                department=user.department
            ).first()
        # --- права действий ---
        can_mark = (
            user.department and
            user.department in departments and
            instance.status != EventStatus.COMPLETED and
            (
                not user_completion or
                user_completion.status != EventStatus.COMPLETED
            )
        )
        can_archive = (
            can_manage_events and
            not event.is_archived
        )
        can_unarchive = (
            can_manage_events and
            event.is_archived
        )
        can_complete = (
            can_manage_events and
            not event.is_archived and
            instance.status != EventStatus.COMPLETED
        )
        # --- подразделения ---
        completions_map = {
            c.department_id: c for c in instance.completions.all()
        }
        departments_info = [
            {
                'department': dept,
                'completion': completions_map.get(dept.id),
                'is_user_department': dept == user.department,
            }
            for dept in departments
        ]
        events_with_actions.append({
            'instance': instance,
            'event': event,
            'document': event.document,  # Добавляем документ
            # computed
            'computed_status': instance.computed_status,
            'days_until_due': instance.days_until_due,
            # permissions
            'user_completion': user_completion,
            'can_mark': can_mark,
            'can_archive': can_archive,
            'can_unarchive': can_unarchive,
            'can_complete': can_complete,
            # data
            'departments_info': departments_info,
        })

    if user.department:
        root = user.department.get_root()
        root_departments = root.get_descendants(include_self=True).order_by('name')
    else:
        root_departments = Department.objects.none()

    statuses = [
        ("completed", 'Выполнено'),
        ("in_work", 'В работе'),
    ]

    template_map = {
        'report': 'plans/reports-events.html',
        'protocol': 'plans/protocols-events.html',
        'order': 'plans/orders-events.html',
        'inspect': 'plans/inspects-events.html',
    }

    doc_type_display = dict(Document.CATEGORY_CHOICES).get(doc_type, doc_type)

    return render(
        request,
        template_map.get(doc_type, 'plans/all-events.html'),
        {
            'doc_type': doc_type,
            'doc_type_display': doc_type_display,
            'events_with_actions': events_with_actions,
            'can_manage_events': can_manage_events,
            'EventStatus': EventStatus,
            'user': user,
            'schedule_types': Event.SCHEDULE_TYPE_CHOICES,
            'period_units': Event.PERIOD_UNIT_CHOICES,
            'departments': root_departments,
            'statuses': statuses,
            'filter': event_filter,
        }
    )
