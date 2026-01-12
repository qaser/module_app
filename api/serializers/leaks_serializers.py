from django.shortcuts import get_object_or_404
from rest_framework import serializers

from equipments.models import Equipment
from leaks.models import Leak, LeakDocument, LeakImage


class LeakImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakImage
        fields = ('id', 'image', 'name',)


class LeakDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakDocument
        fields = ('id', 'doc', 'name',)


class LeakSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = Leak
    fields = (
        'id', 'place', 'equipment', 'specified_location', 'is_valve',
        'description', 'type_leak', 'volume', 'volume_dinamic',
        'gas_losses', 'reason', 'detection_date', 'planned_date',
        'fact_date', 'method', 'detector', 'executor', 'plan_work',
        'doc_name', 'protocol', 'is_done', 'note', 'images', 'files'
    )

    def get_images(self, obj):
        selected_images = LeakImage.objects.filter(leak=obj)
        return LeakImageSerializer(selected_images, many=True).data

    def get_files(self, obj):
        selected_files = LeakDocument.objects.filter(leak=obj)
        return LeakDocumentSerializer(selected_files, many=True).data

    def get_equipment(self, obj):
        equipment = get_object_or_404(Equipment, id=obj.location.id)
        return equipment.name
