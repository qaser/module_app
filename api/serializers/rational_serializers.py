from rest_framework import serializers

from api.serializers.users_serializers import UserSerializer
from rational.models import (AnnualPlan, Proposal, ProposalDocument,
                             ProposalStatus, QuarterlyPlan)
from users.models import ModuleUser, Role, UserAppRoute


class ProposalDocumentSerializer(serializers.ModelSerializer):
    proposal_id = serializers.PrimaryKeyRelatedField(
        queryset=Proposal.objects.all(),
        source='proposal'
    )
    class Meta:
        model = ProposalDocument
        fields = ('id', 'doc', 'name', 'proposal_id')


class ProposalDocumentSerializer(serializers.ModelSerializer):
    proposal_id = serializers.PrimaryKeyRelatedField(
        queryset=Proposal.objects.all(),
        source='proposal'
    )
    class Meta:
        model = ProposalDocument
        fields = ('id', 'doc', 'name', 'proposal_id')


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
