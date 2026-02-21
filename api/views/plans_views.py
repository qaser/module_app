from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from api.serializers.plans_serializers import (
    EventInstanceSerializer, EventSerializer, DocumentSerializer, OrderActivitySerializer, OrderSerializer,
    ProtocolActivityResponsibilitySerializer, ProtocolActivitySerializer,
    ProtocolSerializer)
from equipments.models import Department
from plans.models import (Document, Event, EventInstance, Order, OrderActivity, OrderActivityResponsibility,
                          Protocol, ProtocolActivity, EventStatus, EventCompletion,
                          ProtocolActivityResponsibility)
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, F
from datetime import timedelta


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet для документов"""
    queryset = Document.objects.all().order_by('-date_doc', '-id')
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'subject', 'is_complete', 'is_archived']
    search_fields = ['title', 'num_doc', 'subject']
    ordering_fields = ['date_doc', 'num_doc', 'title']
    ordering = ['-date_doc']

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'retrieve':
            return DocumentSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по документам"""
        queryset = self.filter_queryset(self.get_queryset())

        stats = {
            'total_documents': queryset.count(),
            'active_documents': queryset.filter(is_archived=False).count(),
            'completed_documents': queryset.filter(is_complete=True).count(),
            'archived_documents': queryset.filter(is_archived=True).count(),
            'by_category': {},
            'by_subject': {},
        }

        # Статистика по категориям
        for category_value, category_display in Document.CATEGORY_CHOICES:
            count = queryset.filter(category=category_value).count()
            if count > 0:
                stats['by_category'][category_value] = {
                    'display': category_display,
                    'count': count
                }

        # Статистика по направлениям
        subjects = queryset.values('subject').annotate(count=Count('id'))
        for item in subjects:
            stats['by_subject'][item['subject']] = item['count']

        serializer = DocumentStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Архивировать документ"""
        document = self.get_object()
        document.is_archived = True
        document.save()

        # Архивируем все мероприятия документа
        document.events.update(is_archived=True)

        return Response({'status': 'document archived'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Восстановить документ из архива"""
        document = self.get_object()
        document.is_archived = False
        document.save()
        return Response({'status': 'document restored'})


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet для мероприятий"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def perform_create(self, serializer):
        """Создание мероприятия с текущим пользователем в качестве владельца"""
        serializer.save(owner=self.request.user)


class EventInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet для экземпляров мероприятий"""
    queryset = EventInstance.objects.all()
    serializer_class = EventInstanceSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archived = not instance.is_archived
        instance.save(update_fields=['is_archived'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='mark')
    def mark_event(self, request, pk=None):
        instance = self.get_object()
        user = request.user

        # Проверка: пользователь должен быть из одного из подразделений мероприятия
        user_department = user.department
        if not user_department or not instance.event.departments.filter(id=user_department.id).exists():
            return Response(
                {'error': 'Вы не можете отчитаться за это подразделение.'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Получаем данные
        data = request.data
        status_value = data.get('status')
        actual_completion_date = data.get('actual_completion_date')
        comment = data.get('comment', '')

        # Если статус COMPLETED и нет даты - устанавливаем текущую дату
        if status_value == EventStatus.COMPLETED and not actual_completion_date:
            actual_completion_date = timezone.now().date()
        # Получаем или создаём EventCompletion
        completion, created = EventCompletion.objects.update_or_create(
            instance=instance,
            department=user_department,
            defaults={
                'status': status_value,
                'actual_completion_date': actual_completion_date,
                'comment': comment,
                'assigned_by': user
            }
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='complete')
    def complete_all(self, request, pk=None):
        instance = self.get_object()
        user = request.user
        # data = request.data
        actual_completion_date = timezone.now().date()
        comment = ''
        # Создаем/обновляем все EventCompletion
        for department in instance.event.departments.all():
            EventCompletion.objects.update_or_create(
                instance=instance,
                department=department,
                defaults={
                    'status': EventStatus.COMPLETED,
                    'actual_completion_date': actual_completion_date,
                    'comment': comment,
                    'assigned_by': user
                }
            )
        return Response({
            'status': 'completed',
            'departments_count': instance.event.departments.count(),
            'instance_status': instance.status
        })


class ProtocolViewSet(viewsets.ModelViewSet):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer

    def get_queryset(self):
        """
        Фильтрация по is_archive:
        - По умолчанию — только неархивные
        - ?is_archive=true — только архивные
        - ?all=true — все (включая архивные)
        """
        qs = Protocol.objects.all()
        is_archive = self.request.query_params.get('is_archive')
        show_all = self.request.query_params.get('all')

        if is_archive == 'true':
            qs = qs.filter(is_archive=True)
        elif show_all != 'true':
            # По умолчанию — только активные
            qs = qs.filter(is_archive=False)

        return qs.order_by('-date_protocol', 'num_protocol')

    def perform_create(self, serializer):
        """При создании is_complete=False по умолчанию, is_archive=False"""
        serializer.save(is_complete=False, is_archive=False)

    def destroy(self, request, *args, **kwargs):
        """
        Не удаляем, а архивируем (is_archive = True)
        """
        instance = self.get_object()
        instance.is_archive = True
        instance.save(update_fields=['is_archive'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProtocolsActivitiesViewSet(viewsets.ModelViewSet):
    serializer_class = ProtocolActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем только неархивированные, если не указано иное
        return ProtocolActivity.objects.filter(is_archived=False).prefetch_related(
            'departments',
            'responsibilities__department'
        )

    def get_object(self):
        # Получаем объект, даже если он архивированный (для детального просмотра)
        queryset = ProtocolActivity.objects.all()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Переключаем значение is_archived на противоположное
        instance.is_archived = not instance.is_archived
        instance.save(update_fields=['is_archived', 'last_status_check'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 🟡 PATCH — отметка выполнения (обновление ответственности)
    @action(detail=True, methods=['patch'], url_path='mark')
    def mark_activity(self, request, pk=None):
        activity = self.get_object()
        # Проверка: пользователь должен быть из одного из подразделений мероприятия
        user_dept = request.user.department
        if not user_dept or not activity.departments.filter(id=user_dept.id).exists():
            return Response(
                {'error': 'Вы не можете отчитаться за это подразделение.'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Получаем данные
        data = request.data
        actual_completion_date = data.get('actual_completion_date')
        comment = data.get('comment')
        # Определяем статус: для не-датовых — 'mark', для датовых — 'completed'
        status_value = 'completed' if activity.deadline_type == 'date' else 'mark'
        # Получаем или создаём ответственность
        ProtocolActivityResponsibility.objects.update_or_create(
            activity=activity,
            department=user_dept,
            defaults={
                'status': status_value,
                'actual_completion_date': actual_completion_date,
                'comment': comment,
            }
        )
        # Возвращаем обновлённые данные
        serializer = self.get_serializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = Order.objects.all()
        is_archive = self.request.query_params.get('is_archive')
        show_all = self.request.query_params.get('all')
        if is_archive == 'true':
            qs = qs.filter(is_archive=True)
        elif show_all != 'true':
            # По умолчанию — только активные
            qs = qs.filter(is_archive=False)
        return qs.order_by('-date_order', 'num_order')

    def perform_create(self, serializer):
        serializer.save(is_complete=False, is_archive=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True
        instance.save(update_fields=['is_archive'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersActivitiesViewSet(viewsets.ModelViewSet):
    serializer_class = OrderActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderActivity.objects.filter(is_archived=False).prefetch_related(
            'departments',
            'responsibilities__department'
        )

    def get_object(self):
        queryset = OrderActivity.objects.all()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Переключаем значение is_archived на противоположное
        instance.is_archived = not instance.is_archived
        instance.save(update_fields=['is_archived', 'last_status_check'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='mark')
    def mark_activity(self, request, pk=None):
        activity = self.get_object()
        user_dept = request.user.department
        if not user_dept or not activity.departments.filter(id=user_dept.id).exists():
            return Response(
                {'error': 'Вы не можете отчитаться за это подразделение.'},
                status=status.HTTP_403_FORBIDDEN
            )
        data = request.data
        actual_completion_date = data.get('actual_completion_date')
        comment = data.get('comment')
        status_value = 'completed' if activity.deadline_type == 'date' else 'mark'
        OrderActivityResponsibility.objects.update_or_create(
            activity=activity,
            department=user_dept,
            defaults={
                'status': status_value,
                'actual_completion_date': actual_completion_date,
                'comment': comment,
            }
        )
        serializer = self.get_serializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)
