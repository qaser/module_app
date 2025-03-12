import datetime as dt

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django.http import JsonResponse

from equipments.models import Equipment
from leaks.models import Leak
from rational.models import AnnualPlan, QuarterlyPlan, Proposal, ProposalDocument, Status
from tpa.models import (Factory, Service, ServiceType, Valve, ValveDocument,
                        ValveImage, Work, WorkService)
from users.models import ModuleUser, Role

from .serializers import (AnnualPlanSerializer, EquipmentSerializer,
                          FactorySerializer, LeakSerializer,
                          ProposalDocumentSerializer, ProposalSerializer,
                          QuarterlyPlanSerializer, ServiceSerializer,
                          ServiceTypeSerializer, StatusSerializer,
                          UserSerializer, ValveDocumentSerializer,
                          ValveImageSerializer, ValveSerializer,
                          WorkServiceSerializer)


class ValveImageViewSet(viewsets.ModelViewSet):
    queryset = ValveImage.objects.all()
    serializer_class = ValveImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()


class ValveDocumentViewSet(viewsets.ModelViewSet):
    queryset = ValveDocument.objects.all()
    serializer_class = ValveDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()


class ProposalDocumentViewSet(viewsets.ModelViewSet):
    queryset = ProposalDocument.objects.all()
    serializer_class = ProposalDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()


class LeaksViewSet(viewsets.ModelViewSet):
    queryset = Leak.objects.all()
    serializer_class = LeakSerializer


class ValveViewSet(viewsets.ModelViewSet):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer
    parser_classes = (MultiPartParser, FormParser)

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


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = ModuleUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

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


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

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

    def get_valve(self):  # DRY function for extract 'id' from url and check
        valve = get_object_or_404(Valve, id=self.kwargs['valve_id'])
        return valve

    def get_queryset(self):
        self.get_valve().services.all()
        return self.get_valve().services.all()


class EquipmentViewSet(viewsets.ViewSet):
    def list(self, request):
        parent_id = request.query_params.get('parent_id', None)
        filter_structure = request.query_params.get('filter_structure', 'true')  # По умолчанию фильтруем
        queryset = Equipment.objects.all()
        # Применяем фильтр по parent_id, если он указан
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        # Применяем фильтр по structure, если filter_structure=True
        if filter_structure.lower() == 'true':
            queryset = queryset.filter(structure='Административная структура')
        # Возвращаем данные в формате JSON
        children = queryset.values('id', 'name')
        return Response(list(children))


class StatusViewSet(viewsets.ViewSet):
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


class QuarterlyPlanViewSet(viewsets.ModelViewSet):
    queryset = QuarterlyPlan.objects.all()
    serializer_class = QuarterlyPlanSerializer



# def annual_plans_list(request):
#     """Выдает все годовые планы в виде иерархии."""
#     def serialize_plan(plan):
#         children = plan.equipment.get_children()
#         return {
#             "id": plan.id,
#             "equipment": {"id": plan.equipment.id, "name": plan.equipment.name},
#             "year": plan.year,
#             "total_proposals": plan.total_proposals,
#             "total_economy": plan.total_economy,
#             "children": [serialize_plan(AnnualPlan.objects.get(equipment=child, year=plan.year)) for child in children if AnnualPlan.objects.filter(equipment=child, year=plan.year).exists()]
#         }

#     root_plans = AnnualPlan.objects.filter(equipment__parent__isnull=True)
#     return JsonResponse([serialize_plan(plan) for plan in root_plans], safe=False)

# def quarterly_plan_detail(request, annual_plan_id):
#     """Выдает квартальный план для указанного годового плана."""
#     annual_plan = get_object_or_404(AnnualPlan, id=annual_plan_id)
#     quarterly_plans = QuarterlyPlan.objects.filter(annual_plan=annual_plan)

#     result = []
#     for plan in quarterly_plans:
#         result.append({
#             "equipment_name": plan.annual_plan.equipment.name,
#             "q1": plan.planned_proposals if plan.quarter == 1 else 0,
#             "q2": plan.planned_proposals if plan.quarter == 2 else 0,
#             "q3": plan.planned_proposals if plan.quarter == 3 else 0,
#             "q4": plan.planned_proposals if plan.quarter == 4 else 0,
#         })

#     return JsonResponse(result, safe=False)
