from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.leaks_serializers import LeakSerializer
from api.serializers.rational_serializers import (AnnualPlanSerializer,
                                                  ProposalDocumentSerializer,
                                                  ProposalSerializer,
                                                  QuarterlyPlanSerializer,
                                                  StatusSerializer)
from leaks.models import Leak
from rational.models import (AnnualPlan, Proposal, ProposalDocument,
                             ProposalStatus, QuarterlyPlan)


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


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]


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
