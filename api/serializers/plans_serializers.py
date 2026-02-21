from rest_framework import serializers
import datetime as dt

from api.serializers.equipments_serializers import DepartmentSerializer
from api.serializers.users_serializers import UserSerializer
from equipments.models import Department
from plans.models import (Document, Event, EventCompletion, EventInstance, EventStatus, Order, OrderActivity, OrderActivityResponsibility,
                          Protocol, ProtocolActivity, ProtocolActivityResponsibility, Report, ReportStatus)
from django.utils import timezone


class EventSerializer(serializers.ModelSerializer):
    """Сериализатор для шаблонов мероприятий"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    departments = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        many=True,
        write_only=True,
        # source='departments'
    )
    instances_count = serializers.SerializerMethodField()
    active_instances_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'document',
            'owner',
            'owner_name',
            'description',
            'departments',
            'schedule_type',
            'period_unit',
            'period_interval',
            'start_date',
            'due_date',
            'is_archived',
            'instances_count',
            'active_instances_count',
        ]
        read_only_fields = ['owner', 'instances_count', 'active_instances_count']
        extra_kwargs = {
            'period_interval': {'required': False, 'allow_null': True},
            'start_date': {'required': False, 'allow_null': True},
            'due_date': {'required': False, 'allow_null': True},
            'period_unit': {'required': False, 'allow_null': True},
        }

    def to_internal_value(self, data):
        """Преобразуем входящие данные перед валидацией"""
        # Создаем копию данных для обработки
        processed_data = data.copy()

        # Обрабатываем числовые поля
        numeric_fields = ['period_interval', 'relative_day']
        for field in numeric_fields:
            if field in processed_data:
                value = processed_data[field]
                if value == '' or value is None:
                    processed_data[field] = None
                else:
                    try:
                        # Пробуем преобразовать в число
                        processed_data[field] = int(value)
                    except (ValueError, TypeError):
                        # Если не удалось - оставляем как есть, DRF сам покажет ошибку
                        pass

        # Обрабатываем даты
        date_fields = ['start_date', 'due_date']
        for field in date_fields:
            if field in processed_data:
                value = processed_data[field]
                if value == '' or value is None:
                    processed_data[field] = None

        # Обрабатываем выборные поля
        choice_fields = ['period_unit', 'relative_base', 'relative_position']
        for field in choice_fields:
            if field in processed_data:
                value = processed_data[field]
                if value == '' or value is None:
                    processed_data[field] = None

        return super().to_internal_value(processed_data)

    def validate(self, data):
        """Валидация данных мероприятия"""
        schedule_type = data.get('schedule_type', self.instance.schedule_type if self.instance else 'once')

        # Очищаем неиспользуемые поля в зависимости от типа расписания
        self._clean_unused_fields(data, schedule_type)

        # Валидация обязательных полей для каждого типа расписания
        validation_errors = {}

        if schedule_type == 'once':
            validation_errors.update(self._validate_once(data))
        elif schedule_type == 'periodic':
            validation_errors.update(self._validate_periodic(data))
        # elif schedule_type == 'relative':
        #     validation_errors.update(self._validate_relative(data))
        elif schedule_type == 'continuous':
            validation_errors.update(self._validate_continuous(data))

        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        return data

    def _clean_unused_fields(self, data, schedule_type):
        """Очищает поля, которые не используются для текущего типа расписания"""
        # Для каждого типа расписания очищаем неиспользуемые поля
        field_groups = {
            'once': ['period_unit', 'period_interval', 'start_date'],
            'periodic': ['due_date'],
            # 'relative': ['due_date', 'period_unit', 'period_interval', 'start_date'],
            'continuous': ['due_date', 'period_unit', 'period_interval', 'start_date']
        }

        if schedule_type in field_groups:
            for field in field_groups[schedule_type]:
                if field in data:
                    data[field] = None

    def _validate_once(self, data):
        """Валидация для фиксированной даты"""
        errors = {}

        if not data.get('due_date'):
            errors['due_date'] = 'Для мероприятий с фиксированной датой необходимо указать срок исполнения'

        return errors

    def _validate_periodic(self, data):
        """Валидация для периодических мероприятий"""
        errors = {}
        if not data.get('period_unit'):
            errors['period_unit'] = 'Для периодических мероприятий необходимо указать единицу периода'
        if not data.get('period_interval'):
            errors['period_interval'] = 'Для периодических мероприятий необходимо указать интервал периодичности'
        elif data['period_interval'] is not None and data['period_interval'] < 1:
            errors['period_interval'] = 'Интервал периодичности должен быть положительным числом'
        if not data.get('start_date'):
            errors['start_date'] = 'Для периодических мероприятий необходимо указать дату начала периода'
        return errors

    # def _validate_relative(self, data):
    #     """Валидация для относительных мероприятий"""
    #     errors = {}

    #     if not data.get('relative_base'):
    #         errors['relative_base'] = 'Для относительных мероприятий необходимо указать базовую дату'

    #     if not data.get('relative_position'):
    #         errors['relative_position'] = 'Для относительных мероприятий необходимо указать позицию'

    #     if data.get('relative_day') is None:
    #         errors['relative_day'] = 'Для относительных мероприятий необходимо указать смещение'
    #     elif data['relative_day'] is not None and data['relative_day'] < 0:
    #         errors['relative_day'] = 'Смещение не может быть отрицательным'

    #     return errors

    def _validate_continuous(self, data):
        """Валидация для непрерывных мероприятий"""
        errors = {}

        # Для continuous не должно быть дополнительных полей
        problematic_fields = []
        for field in ['due_date', 'period_unit', 'period_interval', 'start_date']:
            if data.get(field) not in [None, '']:
                problematic_fields.append(field)

        if problematic_fields:
            errors['schedule_type'] = f'Для типа "continuous" не должны быть заполнены поля: {", ".join(problematic_fields)}'

        return errors

    # def _validate_dates(self, data, schedule_type):
    #     """Общая валидация дат"""
    #     errors = {}
    #     today = timezone.now().date()

    #     if data.get('due_date'):
    #         try:
    #             if data['due_date'] < today:
    #                 errors['due_date'] = 'Срок исполнения не может быть в прошлом при создании'
    #         except (TypeError, ValueError):
    #             # Если дата некорректная - DRF уже покажет ошибку формата
    #             pass

    #     if data.get('start_date'):
    #         try:
    #             if data['start_date'] < today:
    #                 errors['start_date'] = 'Дата начала периода не может быть в прошлом при создании'
    #         except (TypeError, ValueError):
    #             pass

    #     return errors

    def get_instances_count(self, obj):
        return obj.instances.count()

    def get_active_instances_count(self, obj):
        return obj.instances.filter(is_archived=False).count()

    def create(self, validated_data):
        """Создание мероприятия"""
        # Устанавливаем владельца (текущего пользователя)
        request = self.context.get('request')
        if request and request.user:
            validated_data['owner'] = request.user

        departments = validated_data.pop('departments', [])

        # Убедимся, что все неиспользуемые поля установлены в None
        schedule_type = validated_data.get('schedule_type', 'once')
        self._clean_unused_fields(validated_data, schedule_type)

        event = Event.objects.create(**validated_data)

        if departments:
            event.departments.set(departments)

        return event

    def update(self, instance, validated_data):
        """Обновление мероприятия"""
        departments = validated_data.pop('departments', None)

        # Убедимся, что все неиспользуемые поля установлены в None
        schedule_type = validated_data.get('schedule_type', instance.schedule_type)
        self._clean_unused_fields(validated_data, schedule_type)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if departments is not None:
            instance.departments.set(departments)

        return instance


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для документов"""
    full_title = serializers.ReadOnlyField()
    events_count = serializers.SerializerMethodField()
    active_events_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'category',
            'category_display',
            'title',
            'full_title',
            'num_doc',
            'date_doc',
            'subject',
            'is_complete',
            'is_archived',
            'events_count',
            'active_events_count',
        ]
        read_only_fields = ['full_title', 'is_complete']
        extra_kwargs = {
            'category_display': {'source': 'get_category_display', 'read_only': True}
        }

    def get_events_count(self, obj):
        """Количество мероприятий в документе"""
        return obj.events.count()

    def get_active_events_count(self, obj):
        """Количество активных мероприятий в документе"""
        return obj.events.filter(is_archived=False).count()

    def validate(self, data):
        """Валидация данных документа"""
        if data.get('num_doc') and not data.get('date_doc'):
            raise serializers.ValidationError(
                {'date_doc': 'При указании номера документа необходимо указать дату'}
            )
        return data

    def create(self, validated_data):
        print(validated_data)
        """Создание документа"""
        # Добавляем пользователя, если нужно
        user = self.context.get('request').user if self.context.get('request') else None
        document = Document.objects.create(**validated_data)
        # Здесь можно добавить логику аудита или уведомлений
        return document


class EventInstanceSerializer(serializers.ModelSerializer):
    """Сериализатор для экземпляров мероприятий"""
    event_description = serializers.CharField(source='event.description', read_only=True)
    event_departments = DepartmentSerializer(source='event.departments.all', many=True, read_only=True)
    document_info = serializers.SerializerMethodField()
    computed_status = serializers.ReadOnlyField()
    computed_status_display = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    status_css_class = serializers.ReadOnlyField()
    completions_count = serializers.SerializerMethodField()
    completed_completions_count = serializers.SerializerMethodField()

    class Meta:
        model = EventInstance
        fields = [
            'id',
            'event',
            'event_description',
            'event_departments',
            'document_info',
            'due_date',
            'status',
            'status_display',
            'computed_status',
            'computed_status_display',
            'days_until_due',
            'status_css_class',
            'completed_at',
            'is_archived',
            'completions_count',
            'completed_completions_count',
        ]
        read_only_fields = [
            'computed_status',
            'computed_status_display',
            'days_until_due',
            'status_css_class'
        ]
        extra_kwargs = {
            'status_display': {'source': 'get_status_display', 'read_only': True}
        }

    def get_document_info(self, obj):
        """Информация о документе"""
        if obj.event.document:
            return {
                'id': obj.event.document.id,
                'title': obj.event.document.title,
                'full_title': obj.event.document.full_title,
                'category': obj.event.document.get_category_display(),
            }
        return None

    def get_completions_count(self, obj):
        """Количество выполнений мероприятия"""
        return obj.completions.count()

    def get_completed_completions_count(self, obj):
        """Количество завершенных выполнений"""
        return obj.completions.filter(status=EventStatus.COMPLETED).count()

    def validate(self, data):
        """Валидация экземпляра мероприятия"""
        # Не позволяем менять статус напрямую
        if 'status' in data and self.instance:
            if self.instance.status != data['status']:
                raise serializers.ValidationError({
                    'status': 'Статус EventInstance изменяется автоматически через EventCompletion'
                })

        # Проверка даты выполнения
        if data.get('due_date'):
            if data['due_date'] < timezone.now().date() and not self.instance:
                raise serializers.ValidationError({
                    'due_date': 'Нельзя создать экземпляр с просроченной датой'
                })

        return data


class EventCompletionSerializer(serializers.ModelSerializer):
    """Сериализатор для выполнения мероприятий подразделениями"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    instance_info = serializers.SerializerMethodField()
    event_info = serializers.SerializerMethodField()
    document_info = serializers.SerializerMethodField()
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EventCompletion
        fields = [
            'id',
            'instance',
            'instance_info',
            'event_info',
            'document_info',
            'department',
            'department_name',
            'status',
            'status_display',
            'actual_completion_date',
            'comment',
            'assigned_by',
            'assigned_by_name',
            'assigned_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['assigned_by', 'assigned_at', 'assigned_by_name']

    def get_instance_info(self, obj):
        """Информация об экземпляре мероприятия"""
        return {
            'id': obj.instance.id,
            'due_date': obj.instance.due_date,
            'status': obj.instance.status,
            'computed_status': obj.instance.computed_status,
        }

    def get_event_info(self, obj):
        """Информация о мероприятии"""
        return {
            'id': obj.instance.event.id,
            'description': obj.instance.event.description,
            'schedule_type': obj.instance.event.get_schedule_type_display(),
        }

    def get_document_info(self, obj):
        """Информация о документе"""
        if obj.instance.event.document:
            return {
                'id': obj.instance.event.document.id,
                'full_title': obj.instance.event.document.full_title,
            }
        return None

    def validate(self, data):
        """Валидация выполнения мероприятия"""
        # Проверка, что подразделение относится к мероприятию
        if 'department' in data and self.instance:
            event_departments = self.instance.instance.event.departments.all()
            if data['department'] not in event_departments:
                raise serializers.ValidationError({
                    'department': f'Подразделение не относится к данному мероприятию. '
                                 f'Допустимые подразделения: {", ".join([str(d) for d in event_departments])}'
                })

        # Проверка даты выполнения
        if data.get('actual_completion_date'):
            if data['actual_completion_date'] > timezone.now().date():
                raise serializers.ValidationError({
                    'actual_completion_date': 'Фактическая дата выполнения не может быть в будущем'
                })

            # Если указана фактическая дата выполнения, статус должен быть COMPLETED
            if data.get('status') != EventStatus.COMPLETED:
                raise serializers.ValidationError({
                    'status': 'При указании фактической даты выполнения статус должен быть "Выполнено"'
                })

        # Проверка статуса
        if data.get('status') == EventStatus.COMPLETED:
            if not data.get('actual_completion_date'):
                data['actual_completion_date'] = timezone.now().date()

        return data

    def create(self, validated_data):
        """Создание выполнения мероприятия"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['assigned_by'] = request.user

        # Проверяем, существует ли уже выполнение для этого подразделения и экземпляра
        instance = validated_data.get('instance')
        department = validated_data.get('department')

        if EventCompletion.objects.filter(instance=instance, department=department).exists():
            raise serializers.ValidationError({
                'non_field_errors': [
                    f'Выполнение мероприятия для подразделения {department} уже существует'
                ]
            })

        event_completion = EventCompletion.objects.create(**validated_data)

        # Обновляем статус экземпляра мероприятия
        event_completion.instance.recalc_event_instance_status()

        return event_completion

    def update(self, instance, validated_data):
        """Обновление выполнения мероприятия"""
        # Сохраняем старый статус для проверки изменений
        old_status = instance.status

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Если изменился статус, обновляем статус экземпляра
        if old_status != instance.status:
            instance.instance.recalc_event_instance_status()

        return instance


# === Сериализаторы для списков и детальных представлений ===

class DocumentDetailSerializer(DocumentSerializer):
    """Детальный сериализатор для документа с мероприятиями"""
    events = EventSerializer(many=True, read_only=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['events']


class EventDetailSerializer(EventSerializer):
    """Детальный сериализатор для мероприятия с экземплярами"""
    instances = EventInstanceSerializer(many=True, read_only=True)

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['instances']


class EventInstanceDetailSerializer(EventInstanceSerializer):
    """Детальный сериализатор для экземпляра мероприятия с выполнениями"""
    completions = EventCompletionSerializer(many=True, read_only=True)

    class Meta(EventInstanceSerializer.Meta):
        fields = EventInstanceSerializer.Meta.fields + ['completions']


# === Сериализаторы для статистики ===

class EventStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики по мероприятиям"""
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    overdue = serializers.IntegerField()
    in_work = serializers.IntegerField()
    not_started = serializers.IntegerField()


class DepartmentStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики по подразделениям"""
    department = DepartmentSerializer()
    total_assignments = serializers.IntegerField()
    completed = serializers.IntegerField()
    completion_rate = serializers.FloatField()


# === Вспомогательные сериализаторы ===

class StatusUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления статуса выполнения мероприятия"""
    status = serializers.ChoiceField(choices=EventStatus.CHOICES)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    actual_completion_date = serializers.DateField(required=False)

    def validate(self, data):
        if data['status'] == EventStatus.COMPLETED and not data.get('actual_completion_date'):
            data['actual_completion_date'] = timezone.now().date()
        return data


class EventInstanceCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания экземпляра мероприятия"""
    class Meta:
        model = EventInstance
        fields = ['event', 'due_date', 'status']
        read_only_fields = ['status']

    def create(self, validated_data):
        validated_data['status'] = EventStatus.NOT_STARTED
        return super().create(validated_data)


class ProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protocol
        fields = [
            'id',
            'title',
            'subject',
            'num_protocol',
            'date_protocol',
            'is_complete',
            'is_archive',
        ]
        read_only_fields = ['is_complete']
        extra_kwargs = {
            'title': {'required': True, 'allow_blank': False},
            'subject': {'required': True, 'allow_blank': False},
            'num_protocol': {'required': True, 'allow_blank': False},
            'date_protocol': {'required': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'title',
            'subject',
            'num_order',
            'date_order',
            'is_complete',
            'is_archive',
        ]
        read_only_fields = ['is_complete']
        extra_kwargs = {
            'title': {'required': True, 'allow_blank': False},
            'subject': {'required': True, 'allow_blank': False},
            'num_order': {'required': True, 'allow_blank': False},
            'date_order': {'required': True},
        }


class ReportSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_current_status(self, obj):
        latest_status = obj.statuses.order_by('-period_start').first()
        if latest_status:
            return {
                'status': latest_status.status,
                'due_date': latest_status.due_date,
                'is_overdue': latest_status.is_overdue
            }
        return None


class ReportStatusSerializer(serializers.ModelSerializer):
    report_name = serializers.CharField(source='report.name', read_only=True)
    department_name = serializers.CharField(source='report.department.name', read_only=True)

    class Meta:
        model = ReportStatus
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProtocolActivityResponsibilitySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ProtocolActivityResponsibility
        fields = [
            'id', 'department', 'department_name', 'status', 'status_display',
            'actual_completion_date', 'comment', 'updated_at'
        ]


class ProtocolActivitySerializer(serializers.ModelSerializer):
    responsibilities = ProtocolActivityResponsibilitySerializer(many=True, read_only=True)
    departments_data = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    deadline_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = ProtocolActivity
        fields = [
            'id', 'description', 'deadline_type', 'deadline_date',
            'status', 'status_display', 'protocol',
            'actual_completion_date', 'last_status_check', 'departments',
            'departments_data', 'responsibilities', 'is_archived',
        ]
        read_only_fields = [
            'last_status_check',
            'status',
            'actual_completion_date',
        ]

    def get_departments_data(self, obj):
        return [{'id': d.id, 'name': d.name} for d in obj.departments.all()]

    def validate(self, data):
        # Получаем deadline_type: из data или из instance
        deadline_type = data.get('deadline_type')
        if deadline_type is None and self.instance:
            deadline_type = self.instance.deadline_type

        # Получаем deadline_date: из data или из instance
        deadline_date = data.get('deadline_date')
        # Если тип — "дата", то дата обязательна
        if deadline_type == 'date':
            if not deadline_date:
                raise serializers.ValidationError({
                    'deadline_date': 'Это поле обязательно при типе "Конкретная дата".'
                })
        # Если тип НЕ "дата", то дата должна отсутствовать (быть None)
        else:
            if deadline_date is not None:
                raise serializers.ValidationError({
                    'deadline_date': f'Нельзя указывать дату для типа "{dict(ProtocolActivity.DEADLINE_TYPES).get(deadline_type)}". Оставьте пустым.'
                })
        return data


class OrderActivityResponsibilitySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderActivityResponsibility
        fields = [
            'id', 'department', 'department_name', 'status', 'status_display',
            'actual_completion_date', 'comment', 'updated_at'
        ]


class OrderActivitySerializer(serializers.ModelSerializer):
    responsibilities = OrderActivityResponsibilitySerializer(many=True, read_only=True)
    departments_data = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    deadline_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = OrderActivity
        fields = [
            'id', 'description', 'deadline_type', 'deadline_date',
            'status', 'status_display', 'order',
            'actual_completion_date', 'last_status_check', 'departments',
            'departments_data', 'responsibilities', 'is_archived',
        ]
        read_only_fields = [
            'last_status_check',
            'status',
            'actual_completion_date',
        ]

    def get_departments_data(self, obj):
        return [{'id': d.id, 'name': d.name} for d in obj.departments.all()]

    def validate(self, data):
        deadline_type = data.get('deadline_type')
        if deadline_type is None and self.instance:
            deadline_type = self.instance.deadline_type
        deadline_date = data.get('deadline_date')
        if deadline_type == 'date':
            if not deadline_date:
                raise serializers.ValidationError({
                    'deadline_date': 'Это поле обязательно при типе "Конкретная дата".'
                })
        else:
            if deadline_date is not None:
                raise serializers.ValidationError({
                    'deadline_date': f'Нельзя указывать дату для типа "{dict(ProtocolActivity.DEADLINE_TYPES).get(deadline_type)}". Оставьте пустым.'
                })
        return data
