from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers.leaks_serializers import LeakSerializer
from leaks.models import Leak


class LeaksViewSet(viewsets.ModelViewSet):
    queryset = Leak.objects.all()
    serializer_class = LeakSerializer
    permission_classes = [IsAuthenticated]
