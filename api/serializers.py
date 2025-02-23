from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from leaks.models import Leak, LeakDocument, LeakImage
from locations.models import Department, Direction, Location, Station
from tpa.models import (Factory, Service, ServiceType, Valve, ValveDocument,
                        ValveImage, Work, WorkProof, WorkService)
from users.models import Profile, User


class LeakImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakImage
        fields = ('id', 'image', 'name',)


class LeakDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakDocument
        fields = ('id', 'doc', 'name',)


class ValveImageSerializer(serializers.ModelSerializer):
    valve_id = serializers.PrimaryKeyRelatedField(queryset=Valve.objects.all(), source='valve')

    class Meta:
        model = ValveImage
        fields = ('id', 'image', 'name', 'valve_id')


class ValveDocumentSerializer(serializers.ModelSerializer):
    valve_id = serializers.PrimaryKeyRelatedField(queryset=Valve.objects.all(), source='valve')

    class Meta:
        model = ValveDocument
        fields = ('id', 'doc', 'name', 'valve_id')


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = '__all__'


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    station = StationSerializer()

    class Meta:
        model = Department
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        depth = 4


class LeakSerializer(serializers.ModelSerializer):
    direction = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = Leak
        fields = (
            'id',
            'direction',
            'place',
            'location',
            'specified_location',
            'is_valve',
            'description',
            'type_leak',
            'volume',
            'volume_dinamic',
            'gas_losses',
            'reason',
            'detection_date',
            'planned_date',
            'fact_date',
            'method',
            'detector',
            'executor',
            'plan_work',
            'doc_name',
            'protocol',
            'is_done',
            'note',
            'images',
            'files'
        )

    def get_images(self, obj):
        selected_images = LeakImage.objects.filter(leak=obj)
        return LeakImageSerializer(selected_images, many=True).data

    def get_files(self, obj):
        selected_files = LeakDocument.objects.filter(leak=obj)
        return LeakDocumentSerializer(selected_files, many=True).data

    def get_location(self, obj):
        location = get_object_or_404(Location, id=obj.location.id)
        return location.name

    # def get_department(self, obj):
    #     department = get_object_or_404(Department, id=obj.location.department.id)
    #     return department.name

    # def get_station(self, obj):
    #     station = get_object_or_404(Station, id=obj.location.department.station.id)
    #     return station.name

    def get_direction(self, obj):
        direction = get_object_or_404(Direction, id=obj.location.department.station.direction.id)
        return direction.name



class ProfileSerializer(serializers.ModelSerializer):
    station = StationSerializer()

    class Meta:
        model = Profile
        fields = ('lastname_and_initials', 'job_position', 'station', 'role')


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    patronymic = serializers.SerializerMethodField()
    station = serializers.SerializerMethodField()
    # profile = ProfileSerializer()
    job_position = serializers.SerializerMethodField()
    lastname_and_initials = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'last_name', 'first_name', 'patronymic',
            'lastname_and_initials', 'username', 'email',
            'job_position', 'role', 'station',
        )

    def get_role(self, obj):
        profile = get_object_or_404(Profile, user=obj)
        return profile.role

    def get_job_position(self, obj):
        profile = get_object_or_404(Profile, user=obj)
        return profile.job_position

    def get_lastname_and_initials(self, obj):
        profile = get_object_or_404(Profile, user=obj)
        return profile.lastname_and_initials

    def get_patronymic(self, obj):
        profile = get_object_or_404(Profile, user=obj)
        return profile.patronymic

    def get_station(self, obj):
        profile = get_object_or_404(Profile, user=obj)
        selected_files = get_object_or_404(Station, id=profile.station.id)
        return StationSerializer(selected_files).data


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = '__all__'


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    station = StationSerializer()

    class Meta:
        model = Department
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        depth = 3


class ValveSerializer(serializers.ModelSerializer):
    direction = serializers.SerializerMethodField()
    station = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    factory = serializers.SerializerMethodField()
    drive_factory = serializers.SerializerMethodField('get_factory')
    latest_service = serializers.SerializerMethodField()

    class Meta:
        model = Valve
        fields = ('id', 'direction', 'station', 'department', 'location',
                  'title', 'diameter', 'pressure', 'valve_type',
                  'factory', 'year_made', 'year_exploit', 'tech_number',
                  'factory_number', 'inventory_number', 'lifetime',
                  'remote', 'label', 'material', 'design', 'drive_type',
                  'drive_factory', 'drive_year_exploit', 'description',
                  'images', 'files', 'latest_service')

    def get_images(self, obj):
        selected_images = ValveImage.objects.filter(valve=obj)
        return ValveImageSerializer(selected_images, many=True, required=False).data

    def get_files(self, obj):
        selected_files = ValveDocument.objects.filter(valve=obj)
        return ValveDocumentSerializer(selected_files, many=True, required=False).data

    def get_factory(self, obj):
        factory = get_object_or_404(Factory, id=obj.factory.id)
        factory_name = factory.name
        factory_country = factory.country
        return f'{factory_name}, {factory_country}'

    def get_location(self, obj):
        location = get_object_or_404(Location, id=obj.location.id)
        return location.name

    def get_department(self, obj):
        department = get_object_or_404(Department, id=obj.location.department.id)
        return department.name

    def get_station(self, obj):
        station = get_object_or_404(Station, id=obj.location.department.station.id)
        return station.name

    def get_direction(self, obj):
        direction = get_object_or_404(Direction, id=obj.location.department.station.direction.id)
        return direction.name

    def get_latest_service(self, obj):
        try:
            latest_service = Service.objects.filter(valve=obj).latest('prod_date')
            id = latest_service.id
            service_type = latest_service.service_type.name
            prod_date = latest_service.prod_date.strftime('%d.%m.%Y')
        except ObjectDoesNotExist:
            id = '-'
            service_type = '-'
            prod_date = '-'
        return {
            'id': id,
            'service_type': service_type,
            'prod_date': prod_date
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['factory'] = f"{instance.factory.name}, {instance.factory.country}" if instance.factory else None
        data['drive_factory'] = f"{instance.drive_factory.name}, {instance.drive_factory.country}" if instance.drive_factory else None
        return data


class ProfileSerializer(serializers.ModelSerializer):
    station = StationSerializer()

    class Meta:
        model = Profile
        fields = ('lastname_and_initials', 'job_position', 'station', 'role')


class WorkProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkProof
        fields = '__all__'


class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = '__all__'
        depth = 1


class WorkServiceSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = WorkService
        fields = ('id', 'work', 'done', 'faults', 'files')
        depth = 1

    def get_files(self, obj):
        selected_files = WorkProof.objects.filter(work=obj)
        return WorkProofSerializer(selected_files, many=True).data

    def create(self, validated_data):
        work_service = WorkService.objects.create(
            service=validated_data['service'],
            work=validated_data['work'],
            done=validated_data['done'],
            faults=validated_data['faults'],
        )
        for file in validated_data['files'].values():
            file_type, _ = file.content_type.split('/')
            WorkProof.objects.create(
                work=work_service,
                name=file.name,
                file=file,
                file_type=file_type,
            )
        return work_service

    def update(self, instance, validated_data):
        for file in validated_data['files'].values():
            file_type, _ = file.content_type.split('/')
            WorkProof.objects.create(
                work=instance,
                name=file.name,
                file=file,
                file_type=file_type,
            )
        return super().update(instance, validated_data)


class ServiceSerializer(serializers.ModelSerializer):
    works = WorkServiceSerializer(many=True, read_only=True, source='workservice_set')
    year = serializers.SerializerMethodField('get_year')
    month = serializers.SerializerMethodField('get_month')
    prod_date = serializers.SerializerMethodField('get_date')
    reg_date = serializers.SerializerMethodField('get_date')

    class Meta:
        model = Service
        fields = '__all__'
        depth = 1

    def get_year(self, obj):
        year, _, _ = str(obj.prod_date).split('-')
        return year

    def get_month(self, obj):
        _, month, _ = str(obj.reg_date).split('-')
        return month

    def get_date(self, obj):
        year, month, day = str(obj.prod_date).split('-')
        return f'{day}.{month}.{year}'


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ('name',)


class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = '__all__'
