import datetime as dt

from django.db.models import Max, Min, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.pipelines_serializers import (
    DiagnosticDocumentSerializer, DiagnosticsSerializer, NodeStateSerializer,
    PipeDocumentSerializer, PipeLimitSerializer, PipelineSerializer,
    PipeSerializer, PipeStateSerializer, TubeSerializer,
    TubeVersionDocumentSerializer)
from equipments.models import Department, Equipment
from pipelines.models import (
    DiagnosticDocument, Diagnostics, Node, NodeState, Pipe, PipeDepartment,
    PipeDocument, PipeLimit, Pipeline, PipeState, Tube, TubeVersion,
    TubeVersionDocument)


class PipeDocumentViewSet(viewsets.ModelViewSet):
    queryset = PipeDocument.objects.all()
    serializer_class = PipeDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class TubeVersionDocumentViewSet(viewsets.ModelViewSet):
    queryset = TubeVersionDocument.objects.all()
    serializer_class = TubeVersionDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class DiagnosticDocumentViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticDocument.objects.all()
    serializer_class = DiagnosticDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()



class PipelineViewSet(viewsets.ModelViewSet):
    serializer_class = PipelineSerializer
    permission_classes = [IsAuthenticated]
    queryset = Pipeline.objects.all().order_by('order')

    def get_queryset(self):
        user_department = self.request.user.department
        if not user_department:
            return Pipeline.objects.none()
        # Дерево: корневой департамент и все потомки
        root = user_department.get_root()
        departments = root.get_descendants(include_self=True)
        # Все Pipe, связанные с этими департаментами
        pipe_ids = PipeDepartment.objects.filter(
            department__in=departments
        ).values_list('pipe_id', flat=True)
        # Всё оборудование в этих департаментах
        equipment_ids = Equipment.objects.filter(
            departments__in=departments
        ).values_list('id', flat=True)
        return Pipeline.objects.filter(
            Q(pipes__id__in=pipe_ids) |
            Q(nodes__equipment__in=equipment_ids)
        ).distinct().order_by('order').prefetch_related(
            Prefetch(
                'pipes',
                queryset=Pipe.objects.filter(id__in=pipe_ids)
                .order_by('start_point').prefetch_related('states', 'limits')
            ),
            Prefetch(
                'nodes',
                queryset=Node.objects.filter(
                    Q(equipment__in=equipment_ids) | Q(is_shared=True)
                ).order_by('location_point').prefetch_related(
                    Prefetch(
                        'states',
                        queryset=NodeState.objects.filter(end_date__isnull=True).order_by('-start_date'),
                        to_attr='current_states'
                    )
                )
            )
        )

    def get_serializer_context(self):
        return {'department': self.request.user.department}


class PipeStatesViewSet(viewsets.ModelViewSet):
    queryset = PipeState.objects.all()
    serializer_class = PipeStateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.get('stateData') or request.data  # поддержка обоих форматов
        pipe_id = data.get('id')
        if not pipe_id:
            return Response({'error': 'Pipe ID не указан'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            pipe = Pipe.objects.get(pk=pipe_id)
        except Pipe.DoesNotExist:
            return Response({'error': 'Pipe не найден'}, status=status.HTTP_404_NOT_FOUND)
        new_state = PipeState.objects.create(
            pipe=pipe,
            state_type=data.get('state_type'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            description=data.get('description'),
            created_by=request.user
        )
        serializer = self.get_serializer(new_state)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PipeLimitViewSet(viewsets.ModelViewSet):
    queryset = PipeLimit.objects.all()
    serializer_class = PipeLimitSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.get('limitData') or request.data  # поддержка обоих форматов
        pipe_id = data.get('id')
        if not pipe_id:
            return Response({'error': 'Pipe ID не указан'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            pipe = Pipe.objects.get(pk=pipe_id)
        except Pipe.DoesNotExist:
            return Response({'error': 'Pipe не найден'}, status=status.HTTP_404_NOT_FOUND)
        new_state = PipeLimit.objects.create(
            pipe=pipe,
            pressure_limit=data.get('pressure_limit'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            limit_reason=data.get('limit_reason'),
        )
        serializer = self.get_serializer(new_state)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        data = request.data.get('limitData') or request.data
        pipe_id = data.get('id')
        if not pipe_id:
            return Response({'error': 'Pipe ID не указан'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pipe = Pipe.objects.get(pk=pipe_id)
        except Pipe.DoesNotExist:
            return Response({'error': 'Pipe не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Получаем последнее ограничение для данной трубы
        last_limit = PipeLimit.objects.filter(pipe=pipe).order_by('-id').first()
        if not last_limit:
            return Response({'error': 'Ограничение не найдено'}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем end_date последнего ограничения
        last_limit.end_date = data.get('end_date')
        last_limit.save()

        serializer = self.get_serializer(last_limit)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NodeStatesViewSet(viewsets.ModelViewSet):
    queryset = NodeState.objects.all()
    serializer_class = NodeStateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.get('stateData') or request.data  # поддержка обоих форматов
        node_id = data.get('id')
        if not node_id:
            return Response({'error': 'Узел ID не указан'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            node = Node.objects.get(pk=node_id)
        except Node.DoesNotExist:
            return Response({'error': 'Узел не найден'}, status=status.HTTP_404_NOT_FOUND)
        new_state = NodeState.objects.create(
            node=node,
            state_type=data.get('state_type'),
            description=data.get('description', ''),
            changed_by=request.user
        )
        serializer = self.get_serializer(new_state)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PipeViewSet(viewsets.ModelViewSet):
    queryset = Pipe.objects.all()
    serializer_class = PipeSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]


class TubesViewSet(viewsets.ModelViewSet):
    queryset = Tube.objects.all()
    serializer_class = TubeSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]


class DiagnosticsViewSet(viewsets.ModelViewSet):
    queryset = Diagnostics.objects.all()
    serializer_class = DiagnosticsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
