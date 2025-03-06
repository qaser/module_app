from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from equipments.models import Equipment
from leaks.models import Leak, LeakDocument, LeakImage
from rational.models import Plan, Proposal, ProposalDocument, Status
from tpa.models import (Factory, Service, ServiceType, Valve, ValveDocument,
                        ValveImage, Work, WorkProof, WorkService)
from users.models import ModuleUser, NotificationAppRoute, Role


class LeakImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakImage
        fields = ('id', 'image', 'name',)


class LeakDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakDocument
        fields = ('id', 'doc', 'name',)


class ProposalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalDocument
        fields = ('id', 'doc', 'name',)


class ValveImageSerializer(serializers.ModelSerializer):
    valve_id = serializers.PrimaryKeyRelatedField(
        queryset=Valve.objects.all(),
        source='valve'
    )

    class Meta:
        model = ValveImage
        fields = ('id', 'image', 'name', 'valve_id')


class ValveDocumentSerializer(serializers.ModelSerializer):
    valve_id = serializers.PrimaryKeyRelatedField(
        queryset=Valve.objects.all(),
        source='valve'
    )

    class Meta:
        model = ValveDocument
        fields = ('id', 'doc', 'name', 'valve_id')


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


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


class UserSerializer(serializers.ModelSerializer):
    apps = serializers.SerializerMethodField()

    class Meta:
        model = ModuleUser
        fields = (
            'id', 'last_name', 'first_name', 'patronymic',
            'lastname_and_initials', 'username', 'email',
            'job_position', 'role', 'equipment', 'apps',
        )

    def get_apps(self, obj):
        """Возвращает список приложений, за которые отвечает пользователь"""
        apps = obj.apps.values_list('app_name', flat=True)
        return list(apps) if apps else []


class ValveSerializer(serializers.ModelSerializer):
    equipment = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    factory = serializers.SerializerMethodField()
    drive_factory = serializers.SerializerMethodField('get_factory')
    latest_service = serializers.SerializerMethodField()

    class Meta:
        model = Valve
        fields = ('id', 'equipment',
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

    def get_equipment(self, obj):
        equipment = get_object_or_404(Equipment, id=obj.equipment.id)
        return equipment.name

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
        data['factory'] = f'{instance.factory.name}, {instance.factory.country}' if instance.factory else None
        data['drive_factory'] = f'{instance.drive_factory.name}, {instance.drive_factory.country}' if instance.drive_factory else None
        return data


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


class StatusSerializer(serializers.Serializer):
    current_status = serializers.ChoiceField(choices=Status.StatusChoices.choices, required=False)
    new_status = serializers.ChoiceField(choices=Status.StatusChoices.choices, required=False)
    proposal_id = serializers.IntegerField(required=False)
    note = serializers.CharField(max_length=500, required=False)

    def to_representation(self, instance):
        # Если instance — объект Status, берем его данные
        if isinstance(instance, Status):
            current_status = instance.status
            status_data = {
                'id': instance.id,
                'date_changed': instance.date_changed.strftime('%d.%m.%Y, %H:%M'),
                'status': {
                    'code': instance.status,
                    'label': instance.get_status_display()
                },
                'owner': {
                    'id': instance.owner.id,
                    'last_name': instance.owner.last_name,
                    'first_name': instance.owner.first_name,
                    'patronymic': instance.owner.patronymic,
                    'lastname_and_initials': instance.owner.lastname_and_initials,
                },
                'note': instance.note,
            }
        else:
            # Иначе предполагаем, что instance — это значение из Status.StatusChoices
            current_status = instance
            status_data = {
                'status': {
                    'code': current_status,
                    'label': Status.StatusChoices(current_status).label
                },
                'owner': None,
                'note': None,
                'date_changed': None,
            }

        # Определяем возможные переходы статусов
        status_transitions = {
            Status.StatusChoices.REG: [
                Status.StatusChoices.REWORK,
                Status.StatusChoices.ACCEPT,
                Status.StatusChoices.REJECT
            ],
            Status.StatusChoices.RECHECK: [
                Status.StatusChoices.REWORK,
                Status.StatusChoices.ACCEPT,
                Status.StatusChoices.REJECT
            ],
            Status.StatusChoices.REWORK: [Status.StatusChoices.RECHECK],
            Status.StatusChoices.ACCEPT: [Status.StatusChoices.APPLY],
            Status.StatusChoices.REJECT: [],
            Status.StatusChoices.APPLY: [],
        }
        possible_statuses = status_transitions.get(current_status, [])
        return {
            'current_status': status_data,  # Все данные текущего статуса
            'possible_statuses': [
                {
                    'code': status,
                    'label': Status.StatusChoices(status).label
                } for status in possible_statuses
            ]
        }

    def validate(self, data):
        request_user = self.context['request'].user
        proposal_id = data.get('proposal_id')
        new_status = data.get('new_status')
        if not proposal_id or not new_status:
            raise serializers.ValidationError("Поля 'proposal_id' и 'new_status' обязательны.")
        proposal = Proposal.objects.get(id=proposal_id)
        # Получаем статус REG
        reg_status = proposal.statuses.filter(status=Status.StatusChoices.REG).first()
        reg_owner = reg_status.owner  # Владелец статуса REG
        # Проверяем, является ли пользователь ответственным за приложение
        is_app_responsible = NotificationAppRoute.objects.filter(
            app_name='rational',
            user=request_user
        ).exists()
        # Проверяем, является ли пользователь владельцем REG
        is_reg_owner = reg_owner == request_user
        # Проверяем, является ли пользователь MANAGER в том же equipment или дочерних
        is_manager_same_branch = (
            request_user.role == Role.MANAGER and
            request_user.equipment and
            reg_owner and
            request_user.equipment.get_root() == reg_owner.equipment.get_root()
        )
        if new_status in [Status.StatusChoices.REWORK, Status.StatusChoices.ACCEPT, Status.StatusChoices.REJECT]:
            if not is_app_responsible:
                raise serializers.ValidationError(
                    "Назначать статусы 'REWORK', 'ACCEPT' и 'REJECT' может только ответственный за приложение."
                )
        elif new_status == Status.StatusChoices.RECHECK:
            if not (is_reg_owner or is_manager_same_branch):
                raise serializers.ValidationError(
                    "Назначать статус 'RECHECK' может только владелец статуса 'REG'"
                )
        return data

    def create(self, validated_data):
        proposal_id = validated_data['proposal_id']
        new_status = validated_data['new_status']
        note = validated_data.get('note', '')
        status = Status.objects.create(
            proposal_id=proposal_id,
            status=new_status,
            note=note,
            owner=self.context['request'].user
        )
        return status


class ProposalSerializer(serializers.ModelSerializer):
    authors = UserSerializer(many=True, read_only=True)
    equipment = serializers.SerializerMethodField()
    reg_date = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    is_economy = serializers.SerializerMethodField()
    statuses = StatusSerializer(many=True, read_only=True)

    class Meta:
        model = Proposal
        fields = [
            'id', 'reg_num', 'reg_date', 'authors', 'equipment',
            'category', 'title', 'description', 'is_economy',
            'economy_size', 'note', 'files', 'statuses'
        ]

    def get_reg_date(self, obj):
        return obj.reg_date.strftime('%d.%m.%Y')

    def get_is_economy(self, obj):
        return 'Да' if obj.is_economy else 'Нет'

    def get_equipment(self, obj):
        return obj.equipment.name if obj.equipment else None

    def get_files(self, obj):
        selected_files = ProposalDocument.objects.filter(proposal=obj)
        return ProposalDocumentSerializer(selected_files, many=True).data
