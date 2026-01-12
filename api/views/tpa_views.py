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

from api.serializers.tpa_serializers import (FactorySerializer,
                                             ServiceSerializer,
                                             ServiceTypeSerializer,
                                             ValveDocumentSerializer,
                                             ValveImageSerializer,
                                             ValveSerializer,
                                             WorkServiceSerializer)
from tpa.models import (Factory, Service, ServiceType, Valve, ValveDocument,
                        ValveImage, Work, WorkService)
from users.models import ModuleUser, Role


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
