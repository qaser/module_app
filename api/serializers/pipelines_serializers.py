from rest_framework import serializers

from api.serializers.equipments_serializers import DepartmentSerializer
from api.serializers.users_serializers import UserSerializer
from pipelines.models import (Anomaly, Bend, ComplexPlan, Defect,
                              DiagnosticDocument, Diagnostics, Hole, Node,
                              NodeState, Pipe, PipeDepartment, PipeDocument,
                              PipeLimit, Pipeline, PipeState, PlannedWork,
                              Repair, Tube, TubeUnit, TubeVersion,
                              TubeVersionDocument)


class PipeDocumentSerializer(serializers.ModelSerializer):
    pipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Pipe.objects.all(),
        source='pipe'
    )

    class Meta:
        model = PipeDocument
        fields = ('id', 'doc', 'name', 'pipe_id')


class TubeVersionDocumentSerializer(serializers.ModelSerializer):
    tube_id = serializers.PrimaryKeyRelatedField(
        queryset=TubeVersion.objects.all(),
        source='tube'
    )

    class Meta:
        model = TubeVersionDocument
        fields = ('id', 'doc', 'name', 'tube_id', 'uploaded_at')


class DiagnosticDocumentSerializer(serializers.ModelSerializer):
    diagnostic_id = serializers.PrimaryKeyRelatedField(
        queryset=Diagnostics.objects.all(),
        source='diagnostic'
    )

    class Meta:
        model = DiagnosticDocument
        fields = ('id', 'doc', 'name', 'diagnostic_id', 'uploaded_at')



class PipeSerializer(serializers.ModelSerializer):
    title = DepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Pipe
        fields = ['id', 'pipeline', 'start_point', 'end_point', 'diameter', 'departments']


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
            'end_date'
        ]


class TubeUnitSerializer(serializers.ModelSerializer):
    unit_type_display = serializers.CharField(source="get_unit_type_display", read_only=True)

    class Meta:
        model = TubeUnit
        fields = [
            "id",
            "odometr_data",
            "unit_type",
            "unit_type_display",
            "description",
            "comment",
        ]
        read_only_fields = ["id", "unit_type_display"]


class TubeVersionSerializer(serializers.ModelSerializer):
    version_id = serializers.IntegerField(source="id", read_only=True)
    version_type_display = serializers.CharField(source="get_version_type_display", read_only=True)
    tube_num = serializers.CharField(source="tube.tube_num", read_only=True)
    has_tube_units = serializers.SerializerMethodField()
    tube_units = TubeUnitSerializer(many=True, read_only=True)
    files = TubeVersionDocumentSerializer(many=True, read_only=True, source='tube_docs')

    class Meta:
        model = TubeVersion
        read_only_fields = ["version_id", "tube_num", "version_type_display"]
        fields = [
            "version_id",
            "tube",
            "tube_num",
            "version_type",
            "version_type_display",
            "date",
            "diagnostics",
            "repair",
            "tube_length",
            "thickness",
            "tube_type",
            "diameter",
            "yield_strength",
            "tear_strength",
            "category",
            "reliability_material",
            "working_conditions",
            "reliability_pressure",
            "reliability_coef",
            "impact_strength",
            "steel_grade",
            "weld_position",
            "from_reference_start",
            "to_reference_end",
            "comment",
            "has_tube_units",
            "tube_units",
            "files",
        ]

    def get_has_tube_units(self, obj):
        return obj.tube_units.exists()


class TubeSerializer(serializers.ModelSerializer):
    pipe_name = serializers.CharField(source="pipe", read_only=True)
    files = serializers.SerializerMethodField()
    versions = TubeVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Tube
        fields = [
            "id",
            "pipe",
            "pipe_name",
            "tube_num",
            "active",
            "installed_date",
            "removed_date",
            "files",
            "versions",
        ]
        read_only_fields = ["id", "pipe_name"]

    def get_files(self, obj):
        print(obj)
        """Возвращает файлы последней версии трубы"""
        latest_version = obj.versions.order_by("-date").first()
        if latest_version:
            # Получаем все документы последней версии
            tube_docs = latest_version.tube_docs.all()
            return TubeVersionDocumentSerializer(tube_docs, many=True).data
        return []

    def to_representation(self, instance):
        """Добавляем данные из последней версии TubeVersion"""
        representation = super().to_representation(instance)
        # Получаем последнюю версию
        latest_version = instance.versions.order_by("-date").first()
        if latest_version:
            # Обновляем representation данными из последней версии
            version_serializer = TubeVersionSerializer(latest_version)
            version_data = version_serializer.data
            # Копируем только нужные поля из версии, исключая files (у нас уже есть отдельное поле)
            exclude_fields = ['id', 'tube', 'tube_num', 'files']
            for field in version_data:
                if field not in exclude_fields:
                    representation[field] = version_data[field]
        return representation


class PipeSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    limit = serializers.SerializerMethodField()
    pipeline = serializers.SerializerMethodField()
    last_repair = serializers.SerializerMethodField()
    last_diagnostics = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    tube_count = serializers.SerializerMethodField()
    unit_count = serializers.SerializerMethodField()

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
            'tube_count',
            'unit_count',
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

    def get_tube_count(self, obj):
        """Возвращает количество труб, связанных с участком"""
        return obj.tubes.count()  # Используем related_name='tubes' из модели Tube

    def get_unit_count(self, obj):
        """Возвращает количество элементов, связанных с участком"""
        # Считаем элементы через связанные трубы
        return TubeUnit.objects.filter(tube__tube__pipe=obj).count()


class DiagnosticsSerializer(serializers.ModelSerializer):
    pipeline = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()
    tube_count = serializers.SerializerMethodField()
    unit_count = serializers.SerializerMethodField()
    bend_count = serializers.SerializerMethodField()
    anomaly_count = serializers.SerializerMethodField()
    defects_count = serializers.SerializerMethodField()

    class Meta:
        model = Diagnostics
        fields = [
            'id',
            'pipeline',
            'length',
            'pipes',
            'start_date',
            'end_date',
            'description',
            'files',
            'tube_count',
            'unit_count',
            'bend_count',
            'anomaly_count',
            'defects_count',
        ]

    def get_pipeline(self, obj):
        first_pipe = obj.pipes.first()
        if first_pipe:
            return first_pipe.pipeline.title
        return None

    def get_files(self, obj):
        selected_files = DiagnosticDocument.objects.filter(diagnostic=obj)
        return DiagnosticDocumentSerializer(selected_files, many=True, required=False).data

    def get_tube_count(self, obj):
        return TubeVersion.objects.filter(diagnostics=obj).count()

    def get_unit_count(self, obj):
        return TubeUnit.objects.filter(tube__diagnostics=obj).count()

    def get_bend_count(self, obj):
        return Bend.objects.filter(tube__diagnostics=obj).count()

    def get_anomaly_count(self, obj):
        return Anomaly.objects.filter(tube__diagnostics=obj).count()

    def get_defects_count(self, obj):
        return Defect.objects.filter(tube__diagnostics=obj).count()

    def get_length(self, obj):
        pipes = obj.pipes.all()
        if not pipes:
            return 0
        start = min(pipe.start_point for pipe in pipes)
        end = max(pipe.end_point for pipe in pipes)
        return f'от {start} до {end} км'


class BendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bend
        fields = '__all__'


class AnomalySerializer(serializers.ModelSerializer):
    class Meta:
        model = Anomaly
        fields = '__all__'


class NodeSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    # equipment = EquipmentSerializer()
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
            'equipment',
            'state',
        ]

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
