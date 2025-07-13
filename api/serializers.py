from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from equipments.models import Department, Equipment
from leaks.models import Leak, LeakDocument, LeakImage
from notifications.models import Notification
from pipelines.models import (PipeDepartment, PipeDocument, PipeLimit, Pipeline, Pipe, Node, PipeState, NodeState,
                              ComplexPlan, PlannedWork, Repair,
                              Diagnostics, Hole)
from rational.models import (AnnualPlan, Proposal, ProposalDocument,
                             ProposalStatus, QuarterlyPlan)
from tpa.models import (Factory, Service, ServiceType, Valve, ValveDocument,
                        ValveImage, Work, WorkProof, WorkService)
from users.models import ModuleUser, Role, UserAppRoute


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


class LeakImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakImage
        fields = ('id', 'image', 'name',)


class LeakDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakDocument
        fields = ('id', 'doc', 'name',)


class ProposalDocumentSerializer(serializers.ModelSerializer):
    proposal_id = serializers.PrimaryKeyRelatedField(
        queryset=Proposal.objects.all(),
        source='proposal'
    )
    class Meta:
        model = ProposalDocument
        fields = ('id', 'doc', 'name', 'proposal_id')


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


class PipeDocumentSerializer(serializers.ModelSerializer):
    pipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Pipe.objects.all(),
        source='pipe'
    )

    class Meta:
        model = PipeDocument
        fields = ('id', 'doc', 'name', 'pipe_id')


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
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
            'job_position', 'role', 'department', 'apps',
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
                  'drive_factory', 'drive_year_exploit', 'note',
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
    current_status = serializers.ChoiceField(choices=ProposalStatus.StatusChoices.choices, required=False)
    new_status = serializers.ChoiceField(choices=ProposalStatus.StatusChoices.choices, required=False)
    proposal_id = serializers.IntegerField(required=False)
    note = serializers.CharField(max_length=500, required=False)

    def to_representation(self, instance):
        # Если instance — объект Status, берем его данные
        if isinstance(instance, ProposalStatus):
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
                    'label': ProposalStatus.StatusChoices(current_status).label
                },
                'owner': None,
                'note': None,
                'date_changed': None,
            }
        # Определяем возможные переходы статусов
        status_transitions = {
            ProposalStatus.StatusChoices.REG: [
                ProposalStatus.StatusChoices.REWORK,
                ProposalStatus.StatusChoices.ACCEPT,
                ProposalStatus.StatusChoices.REJECT
            ],
            ProposalStatus.StatusChoices.RECHECK: [
                ProposalStatus.StatusChoices.REWORK,
                ProposalStatus.StatusChoices.ACCEPT,
                ProposalStatus.StatusChoices.REJECT
            ],
            ProposalStatus.StatusChoices.REWORK: [ProposalStatus.StatusChoices.RECHECK],
            ProposalStatus.StatusChoices.ACCEPT: [ProposalStatus.StatusChoices.APPLY],
            ProposalStatus.StatusChoices.REJECT: [],
            ProposalStatus.StatusChoices.APPLY: [],
        }
        possible_statuses = status_transitions.get(current_status, [])
        return {
            'current_status': status_data,  # Все данные текущего статуса
            'possible_statuses': [
                {
                    'code': status,
                    'label': ProposalStatus.StatusChoices(status).label
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
        reg_status = proposal.statuses.filter(status=ProposalStatus.StatusChoices.REG).first()
        reg_owner = reg_status.owner  # Владелец статуса REG
        # Находим корневой department для proposal.department
        root_department = proposal.department
        while root_department.parent:
            root_department = root_department.parent
        # Проверяем, является ли пользователь ответственным за приложение
        is_app_responsible = UserAppRoute.objects.filter(
            app_name='rational',
            department=root_department,  # Используем корневой department
            user=request_user
        ).exists()
        # Проверяем, является ли пользователь владельцем REG
        is_reg_owner = reg_owner == request_user
        # Проверяем, является ли пользователь MANAGER в том же department или дочерних
        is_manager_same_branch = (
            request_user.role == Role.MANAGER and
            request_user.department and
            reg_owner and
            request_user.department.get_root() == reg_owner.department.get_root()
        )
        if new_status in [
            ProposalStatus.StatusChoices.REWORK,
            ProposalStatus.StatusChoices.ACCEPT,
            ProposalStatus.StatusChoices.REJECT
        ]:
            if not is_app_responsible:
                raise serializers.ValidationError(
                    "Назначать статусы 'REWORK', 'ACCEPT' и 'REJECT' может только ответственный за приложение."
                )
        elif new_status == ProposalStatus.StatusChoices.RECHECK:
            if not (is_reg_owner or is_manager_same_branch):
                raise serializers.ValidationError(
                    "Назначать статус 'RECHECK' может только владелец статуса 'REG'"
                )
        return data

    def create(self, validated_data):
        proposal_id = validated_data['proposal_id']
        new_status = validated_data['new_status']
        note = validated_data.get('note', '')
        status = ProposalStatus.objects.create(
            proposal_id=proposal_id,
            status=new_status,
            note=note,
            owner=self.context['request'].user
        )
        return status


class ProposalSerializer(serializers.ModelSerializer):
    authors = UserSerializer(many=True, read_only=True)
    department = serializers.SerializerMethodField()
    reg_date = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    statuses = StatusSerializer(many=True, read_only=True)

    class Meta:
        model = Proposal
        fields = [
            'id', 'reg_num', 'reg_date', 'authors', 'department',
            'category', 'title', 'description', 'is_economy',
            'economy_size', 'note', 'files', 'statuses'
        ]
        read_only_fields = ['reg_date', 'authors', 'department']

    def get_reg_date(self, obj):
        return obj.reg_date.strftime('%d.%m.%Y')

    def get_department(self, obj):
        return obj.department.name if obj.department else None

    def get_files(self, obj):
        selected_files = ProposalDocument.objects.filter(proposal=obj)
        return ProposalDocumentSerializer(selected_files, many=True).data

    def validate(self, data):
        is_economy = data.get('is_economy')
        economy_size = data.get('economy_size')
        if is_economy and (economy_size is not None and economy_size == 0):
            data['is_economy'] = False
        if economy_size is not None and economy_size > 0 and not is_economy:
            data['is_economy'] = True
        return data


class QuarterlyPlanSerializer(serializers.ModelSerializer):
    planned_economy = serializers.SerializerMethodField()
    sum_economy = serializers.SerializerMethodField()

    def get_planned_economy(self, obj):
        return f'{obj.planned_economy / 1000:.1f}'

    def get_sum_economy(self, obj):
        return f'{obj.sum_economy / 1000:.1f}'

    class Meta:
        model = QuarterlyPlan
        fields = [
            'quarter',
            'planned_proposals',
            'planned_economy',
            'completed_proposals',
            'sum_economy',
        ]


class AnnualPlanSerializer(serializers.ModelSerializer):
    quarterly_plans = QuarterlyPlanSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    children_plans = serializers.SerializerMethodField()
    total_economy = serializers.SerializerMethodField()
    sum_economy = serializers.SerializerMethodField()

    class Meta:
        model = AnnualPlan
        fields = [
            'id', 'department', 'department_name', 'year',
            'total_proposals', 'total_economy', 'completed_proposals', 'sum_economy',
            'quarterly_plans', 'children_plans',
        ]

    def get_total_economy(self, obj):
        return f'{obj.total_economy / 1000:.1f}'

    def get_sum_economy(self, obj):
        return f'{obj.sum_economy / 1000:.1f}'

    def get_children_plans(self, obj):
        children_department = obj.department.get_children()
        children_plans = AnnualPlan.objects.filter(
            department__in=children_department,
            year=obj.year
        )
        return AnnualPlanSerializer(children_plans, many=True).data


class PipeDepartmentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )

    class Meta:
        model = PipeDepartment
        fields = ['department_name']


class PipeStateSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()
    state_type_display = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)
    start_date = serializers.DateField(format='%d.%m.%Y')
    end_date = serializers.DateField(format='%d.%m.%Y')

    class Meta:
        model = PipeState
        fields = '__all__'

    def get_color(self, obj):
        return PipeState.STATE_COLORS.get(obj.state_type)

    def get_state_type_display(self, obj):
        return obj.get_state_type_display()


class NodeStateSerializer(serializers.ModelSerializer):
    state_display = serializers.CharField(
        source='get_state_type_display',
        read_only=True
    )
    changed_by = UserSerializer(read_only=True)
    start_date = serializers.DateField(format='%d.%m.%Y')

    class Meta:
        model = NodeState
        fields = '__all__'


class PipeLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipeLimit
        fields = [
            'pressure_limit',
            'limit_reason',
            'start_date',
            # 'end_date'
        ]


class PipeSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    limit = serializers.SerializerMethodField()
    pipeline = serializers.SerializerMethodField()
    last_repair = serializers.SerializerMethodField()
    last_diagnostics = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = Pipe
        fields = [
            'id',
            'pipeline',
            'departments',
            'start_point',
            'end_point',
            'diameter',
            'exploit_year',
            'state',
            'limit',
            'last_repair',
            'last_diagnostics',
            'files',
        ]

    def get_departments(self, obj):
        return [
            {
                'id': pd.department.id,
                'name': pd.department.name,
                'start_point': pd.start_point,
                'end_point': pd.end_point
            }
            for pd in obj.pipedepartment_set.select_related('department')
        ]

    def get_pipeline(self, obj):
        return obj.pipeline.title

    def get_state(self, obj):
        current_state = obj.current_state
        if current_state:
            return PipeStateSerializer(current_state).data
        return None

    def get_limit(self, obj):
        limit = obj.limits.filter(end_date__isnull=True).first()
        if limit:
            return PipeLimitSerializer(limit).data
        return None

    def get_last_repair(self, obj):
        last_repair = obj.pipe_repairs.order_by('-start_date').first()
        if last_repair:
            return {
                'id': last_repair.id,
                'start_date': last_repair.start_date.strftime('%d.%m.%Y') if last_repair.start_date else None,
                'end_date': last_repair.end_date.strftime('%d.%m.%Y') if last_repair.end_date else None
            }
        return None

    def get_last_diagnostics(self, obj):
        last_diagnostics = obj.pipe_diagnostics.order_by('-start_date').first()
        if last_diagnostics:
            return {
                'id': last_diagnostics.id,
                'start_date': last_diagnostics.start_date.strftime('%d.%m.%Y') if last_diagnostics.start_date else None,
                'end_date': last_diagnostics.end_date.strftime('%d.%m.%Y') if last_diagnostics.end_date else None
            }
        return None

    def get_files(self, obj):
        selected_files = PipeDocument.objects.filter(pipe=obj)
        return PipeDocumentSerializer(selected_files, many=True, required=False).data



class NodeSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    # valves = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    node_type_display = serializers.CharField(
        source='get_node_type_display',
        read_only=True
    )

    class Meta:
        model = Node
        fields = [
            'id',
            'node_type',
            'node_type_display',
            'location_point',
            'pipeline',
            'department',
            # 'valves',
            'state',
        ]

    def get_valves(self, obj):
        valves = Valve.objects.filter(equipment=obj.equipment)
        return ValveSerializer(valves, many=True).data

    def get_state(self, obj):
        latest_state = obj.current_states[0] if hasattr(obj, 'current_states') and obj.current_states else None
        if latest_state:
            return NodeStateSerializer(latest_state).data
        return None

    def get_department(self, obj):
        departments = obj.equipment.departments.all()
        if not departments.exists():
            return None
        root_department = departments.order_by('tree_id', 'level').first().get_root()
        return {
            'id': root_department.id,
            'name': root_department.name
        }


class PipelineSerializer(serializers.ModelSerializer):
    pipes = PipeSerializer(many=True)
    nodes = NodeSerializer(many=True)

    class Meta:
        model = Pipeline
        fields = [
            'order',
            'title',
            'description',
            'pipes',
            'nodes'
        ]


class ComplexPlanSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    planned_works_count = serializers.SerializerMethodField()

    class Meta:
        model = ComplexPlan
        fields = [
            'id', 'department', 'department_name', 'year',
            'planned_works_count'
        ]

    def get_planned_works_count(self, obj):
        return obj.planned_works.count()


class PlannedWorkSerializer(serializers.ModelSerializer):
    work_type_display = serializers.CharField(source='get_work_type_display', read_only=True)
    target_object = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = PlannedWork
        fields = [
            'id', 'complex_plan', 'work_type', 'work_type_display',
            'description', 'start_date', 'end_date', 'pipe', 'node',
            'target_object', 'target_type', 'department'
        ]
        extra_kwargs = {
            'pipe': {'required': False, 'allow_null': True},
            'node': {'required': False, 'allow_null': True}
        }

    def get_target_object(self, obj):
        if obj.pipe:
            return PipeSerializer(obj.pipe).data
        elif obj.node:
            return NodeSerializer(obj.node).data
        return None

    def get_target_type(self, obj):
        if obj.pipe:
            return 'pipe'
        elif obj.node:
            return 'node'
        return None

    def get_department(self, obj):
        if obj.pipe:
            return obj.pipe.department.name
        elif obj.node:
            return obj.node.equipment.department.name
        return None

    def validate(self, data):
        if not data.get('pipe') and not data.get('node'):
            raise serializers.ValidationError(
                "Необходимо указать либо участок газопровода, либо крановый узел."
            )
        if data.get('pipe') and data.get('node'):
            raise serializers.ValidationError(
                "Можно указать только один объект - либо участок газопровода, либо крановый узел."
            )
        return data


class RepairSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repair
        fields = '__all__'


class DiagnosticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnostics
        fields = '__all__'


# class DefectSerializer(serializers.ModelSerializer):
#     defect_type_display = serializers.CharField(source='get_defect_type_display', read_only=True)
#     defect_place_display = serializers.CharField(source='get_defect_place_display', read_only=True)

#     class Meta:
#         model = Defect
#         fields = '__all__'


class HoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hole
        fields = '__all__'
