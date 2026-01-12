from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'title',
            'message',
            'url',
            'created_at',
            'is_read',
            'app_name',
            'object_id'
        ]

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_user(self, obj):
        return obj.user.lastname_and_initials
