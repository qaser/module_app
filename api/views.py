import datetime as dt

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q, Max, Min
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from notifications.models import Notification
from .serializers import NotificationSerializer

from equipments.models import Department, Equipment
from leaks.models import Leak
from pipelines.models import Pipeline, Pipe, ValveNode, ConnectionNode, BridgeNode
from rational.models import (AnnualPlan, Proposal, ProposalDocument,
                             QuarterlyPlan, ProposalStatus)
from tpa.models import (Factory, Service, ServiceType, Valve, ValveDocument,
                        ValveImage, Work, WorkService)
from users.models import ModuleUser, Role

from .serializers import (AnnualPlanSerializer, DepartmentSerializer,
                          EquipmentSerializer, FactorySerializer,
                          LeakSerializer, ProposalDocumentSerializer,
                          ProposalSerializer, QuarterlyPlanSerializer,
                          ServiceSerializer, ServiceTypeSerializer,
                          StatusSerializer, UserSerializer,
                          ValveDocumentSerializer, ValveImageSerializer,
                          ValveSerializer, WorkServiceSerializer,
                          NotificationSerializer, PipelineSerializer)


class ValveImageViewSet(viewsets.ModelViewSet):
    queryset = ValveImage.objects.all()
    serializer_class = ValveImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ValveDocumentViewSet(viewsets.ModelViewSet):
    queryset = ValveDocument.objects.all()
    serializer_class = ValveDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ProposalDocumentViewSet(viewsets.ModelViewSet):
    queryset = ProposalDocument.objects.all()
    serializer_class = ProposalDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class LeaksViewSet(viewsets.ModelViewSet):
    queryset = Leak.objects.all()
    serializer_class = LeakSerializer
    permission_classes = [IsAuthenticated]


class ValveViewSet(viewsets.ModelViewSet):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        factory_str = self.request.data.get("factory")
        drive_factory_str = self.request.data.get("drive_factory")

        def get_existing_factory(factory_str):
            if not factory_str:
                return None
            parts = factory_str.split(", ")
            name, country = parts
            return Factory.objects.get(name=name, country=country)

        # Преобразуем строки в объекты Factory перед сохранением
        factory = get_existing_factory(factory_str) if factory_str else None
        drive_factory = get_existing_factory(drive_factory_str) if drive_factory_str else None
        # Вызываем метод save() с обновленными полями
        serializer.save(factory=factory, drive_factory=drive_factory)


class FactoryViewSet(viewsets.ModelViewSet):
    queryset = Factory.objects.all()
    serializer_class = FactorySerializer
    permission_classes = [IsAuthenticated]


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = ModuleUser.active_objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated]

    @action(methods=['GET', 'PATCH'], detail=False)
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data)


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.values('name').distinct().order_by('name')
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        valve = get_object_or_404(Valve, id=self.request.data['valve'])
        executor = get_object_or_404(ModuleUser, id=self.request.user.id)
        reg_date = dt.datetime.now().strftime('%Y-%m-%d')
        service_type = get_object_or_404(
            ServiceType,
            valve_type=valve.valve_type,
            name=self.request.data['name'],
            min_diameter__lte=valve.diameter,
            max_diameter__gte=valve.diameter
        )
        works = Work.objects.filter(service_type=service_type, planned=True)
        serializer.save(
            executor=executor,
            prod_date=self.request.data['prod_date'],
            reg_date=reg_date,
            service_type=service_type,
            works=works,
            valve=valve
        )

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        service.delete()
        return Response(data='delete success')


class WorkServiceView(viewsets.ModelViewSet):
    queryset = WorkService.objects.all()
    serializer_class = WorkServiceSerializer
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        instance = self.get_object()
        description = self.request.POST['description']
        done = True if self.request.POST['done'] == 'true' else False
        faults = self.request.POST['faults']
        work_planned = True if self.request.POST['planned'] == 'true' else False
        if work_planned is False:
            Work.objects.filter(id=instance.work.id).update(description=description)
        serializer.save(
            done=done,
            faults=faults,
            files=self.request.FILES
        )

    def perform_create(self, serializer):
        description = self.request.POST['description']
        done = True if self.request.POST['done'] == 'true' else False
        faults = self.request.POST['faults']
        service = get_object_or_404(Service, id=self.request.POST['service'])
        work = Work.objects.create(
            description=description,
            service_type=service.service_type,
            planned=False
        )
        serializer.save(
            service=service,
            work=work,
            done=done,
            faults=faults,
            files=self.request.FILES
        )


class ValveServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_valve(self):  # DRY function for extract 'id' from url and check
        valve = get_object_or_404(Valve, id=self.kwargs['valve_id'])
        return valve

    def get_queryset(self):
        self.get_valve().services.all()
        return self.get_valve().services.all()


class EquipmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        parent_id = request.query_params.get('parent_id', None)
        queryset = Equipment.objects.all()
        # Применяем фильтр по parent_id, если он указан
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        # Возвращаем данные в формате JSON
        children = queryset.values('id', 'name')
        return Response(list(children))


class DepartmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        parent_id = request.query_params.get('parent_id', None)
        queryset = Department.objects.all()
        # Применяем фильтр по parent_id, если он указан
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        # Возвращаем данные в формате JSON
        children = queryset.values('id', 'name')
        return Response(list(children))


class StatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        current_status = request.query_params.get('status')
        if not current_status:
            return Response(
                {'error': 'Параметр "status" обязателен.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = StatusSerializer(current_status)
        return Response(serializer.data)

    def create(self, request):
        serializer = StatusSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            status_instance = serializer.save()
            return Response(
                {'message': 'Статус успешно добавлен.', 'status_id': status_instance.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnnualPlanViewSet(viewsets.ModelViewSet):
    queryset = AnnualPlan.objects.all()
    serializer_class = AnnualPlanSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class QuarterlyPlanViewSet(viewsets.ModelViewSet):
    queryset = QuarterlyPlan.objects.all()
    serializer_class = QuarterlyPlanSerializer
    permission_classes = [IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтрация только для текущего пользователя"""
        return self.queryset.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Кастомный эндпоинт для непрочитанных уведомлений"""
        last_check = request.query_params.get('last_check')
        queryset = self.get_queryset().filter(is_read=False)

        if last_check:
            try:
                last_check = timezone.datetime.fromisoformat(last_check)
                queryset = queryset.filter(created_at__gt=last_check)
            except ValueError:
                pass

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Пометить уведомление как прочитанное"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})


class PipelineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PipelineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.department:
            return Pipeline.objects.none()

        # Получаем все участки, связанные с department пользователя
        department_pipes = Pipe.objects.filter(department=user.department)
        pipeline_ids = department_pipes.values_list('pipeline_id', flat=True).distinct()

        # Получаем диапазон километража для отображения
        min_km = department_pipes.aggregate(Min('start_point'))['start_point__min']
        max_km = department_pipes.aggregate(Max('end_point'))['end_point__max']

        # Добавляем небольшой отступ по краям
        self.view_start = min_km - 0.5 if min_km else 0
        self.view_end = max_km + 0.5 if max_km else 10

        return Pipeline.objects.filter(id__in=pipeline_ids)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Добавляем метаданные о диапазоне отображения
        response.data['view_range'] = {
            'start': getattr(self, 'view_start', 0),
            'end': getattr(self, 'view_end', 10)
        }
        return response
