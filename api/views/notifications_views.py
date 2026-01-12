from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.notification_serializers import NotificationSerializer
from notifications.models import Notification


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
