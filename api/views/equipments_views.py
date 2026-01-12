from rest_framework import generics, permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from equipments.models import Department, Equipment


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
