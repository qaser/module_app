from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from equipments.models import Department, Equipment
from notifications.models import Notification
from users.models import ModuleUser, Role, UserAppRoute


class UserSerializer(serializers.ModelSerializer):
    apps = serializers.SerializerMethodField()

    class Meta:
        model = ModuleUser
        fields = (
            'id', 'last_name', 'first_name', 'patronymic',
            'lastname_and_initials', 'username', 'email',
            'job_position', 'role', 'department', 'apps',
        )

    def get_apps(self, obj):
        """Возвращает список приложений, за которые отвечает пользователь"""
        apps = obj.apps.values_list('app_name', flat=True)
        return list(apps) if apps else []
