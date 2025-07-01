import datetime as dt

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from equipments.models import Department, Equipment
from users.models import ModuleUser


class Pipeline(models.Model):
    title = models.CharField('Название газопровода', max_length=100)
    order = models.PositiveSmallIntegerField('Номер газопровода', default=1)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Газопровод'
        verbose_name_plural = 'Газопроводы'

    def __str__(self):
        return self.title


class Pipe(models.Model):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='pipes'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='pipe_departments',
    )
    diameter = models.PositiveIntegerField(
        'Диаметр, мм',
        blank=True,
        null=True
    )
    start_point = models.FloatField(
        verbose_name='Начало участка, км',
        blank=False,
        null=False
    )
    end_point = models.FloatField(
        verbose_name='Конец участка, км',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Участок газопровода'
        verbose_name_plural = 'Участки газопроводов'
        ordering = ['start_point']

    @property
    def current_state(self):
        return self.states.filter(end_date__isnull=True).first()


class PipeRepair(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='repairs'
    )
    start_date = models.DateTimeField(
        verbose_name='Начало ремонта',
        auto_now_add=True
    )
    end_date = models.DateTimeField(
        verbose_name='Окончание ремонта',
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name='Дополнительная информация',
        max_length=500,
        blank=True
    )


class PipeRepairDocument(models.Model):
    hole = models.ForeignKey(
        PipeRepair,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    doc = models.FileField(upload_to='pipelines/docs/')
    title = models.CharField(
        'Наименование документа',
        max_length=50,
        blank=False,
        null=False,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        verbose_name='Дополнительная информация',
        max_length=500,
        blank=True,
    )

    class Meta:
        verbose_name = 'Документация по ремонту участка МГ'
        verbose_name_plural = 'Документация по ремонтам участков МГ'


class PipeRepairStage(models.Model):
    repair = models.ForeignKey(
        PipeRepair,
        on_delete=models.CASCADE,
        related_name='stages'
    )
    stage_date = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True
    )
    title = models.CharField(
        verbose_name='Наименование этапа',
        max_length=50,
        blank=False,
        null=False,
    )
    resource = models.TextField(
        verbose_name='Ресурсы',
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name='Дополнительная информация',
        max_length=500,
        blank=False,
        null=False,
    )


class Hole(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='holes'
    )
    location_point = models.FloatField(
        verbose_name='Место расположения, км',
        blank=False,
        null=False
    )
    cutting_date = models.DateTimeField(
        verbose_name='Дата вырезки',
        null=False,
        blank=False,
    )
    welding_date = models.DateTimeField(
        verbose_name='Дата заварки',
        null=True,
        blank=True,
    )


class HoleDocument(models.Model):
    hole = models.ForeignKey(
        Hole,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    doc = models.FileField(upload_to='pipelines/docs/')
    title = models.CharField(
        'Наименование документа',
        max_length=50,
        blank=False,
        null=False,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        max_length=500,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Документация по ТО'
        verbose_name_plural = 'Документация по ТО'


class PipeState(models.Model):
    STATE_CHOICES = [
        ('repair', 'В ремонте'),
        ('operation', 'В работе'),
        ('disabled', 'Отключен'),
        ('limited', 'Работа с ограничением'),
        ('depletion', 'На выработке'),
        ('diagnostics', 'Проведение ВТД'),
    ]
    STATE_COLORS = {
        'repair': '#FF0000',  # Красный
        'operation': '#00FF00',  # Зеленый
        'disabled': '#888888',  # Серый
        'limited': '#FFFF00',  # Желтый
        'depletion': '#FFA500',  # Оранжевый
        'diagnostics': '#0000FF',  # Синий
    }
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='states'
    )
    state_type = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        verbose_name='Тип состояния'
    )
    start_date = models.DateTimeField(
        verbose_name='Начало состояния',
        auto_now_add=True
    )
    end_date = models.DateTimeField(
        verbose_name='Окончание состояния',
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name='Описание состояния',
        max_length=500,
        blank=True
    )
    created_by = models.ForeignKey(
        ModuleUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Кем создано'
    )
    current_pressure = models.FloatField(
        verbose_name='Давление, МПа'
    )
    is_limited = models.BooleanField(
        verbose_name='С ограничением давления',
        default=False
    )
    pressure_limit = models.FloatField(
        verbose_name='Ограничение давления, МПа'
    )
    limit_reason = models.CharField(
        max_length=100,
        verbose_name='Причина ограничения'
    )

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Состояние участка'
        verbose_name_plural = 'Состояния участков'

    def __str__(self):
        return f"{self.state_type} (участок {self.pipe.id})"

    @property
    def color(self):
        return self.STATE_COLORS.get(self.state_type, '#CCCCCC')

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("Дата окончания не может быть раньше даты начала")


class Node(models.Model):
    TYPE_CHOICES = [
        ('valve', 'Линейный кран'),
        ('host', 'Узел подключения'),
        ('bridge', 'Перемычка'),
        # ('tails', 'Шлейфы'),
        # ('ks', 'КС'),
    ]
    node_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип узла'
    )
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='nodes'
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='node_equipments',
    )
    location_point = models.FloatField(
        verbose_name='Место расположения, км',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Крановый узел'
        verbose_name_plural = 'Крановые узлы'
        ordering = ['location_point']

    @property
    def current_state(self):
        return self.states.filter('timestamp').first()


class NodeState(models.Model):
    NODE_STATES = [
        ('open', 'Открыто'),
        ('closed', 'Закрыто'),
    ]

    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='states'
    )
    state = models.CharField(
        max_length=10,
        choices=NODE_STATES,
        verbose_name='Состояние'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время изменения'
    )
    changed_by = models.ForeignKey(
        ModuleUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Кем изменено'
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Состояние кранового узла'
        verbose_name_plural = 'Состояния крановых узлов'

    def __str__(self):
        return f"{self.node} - {self.get_state_display()}"


# @receiver(pre_save, sender=ValveState)
# def update_valve_states(sender, instance, **kwargs):
#     if not instance.pk:
#         ValveState.objects.filter(
#             valve=instance.valve
#         ).update(is_current=False)


# @receiver(pre_save, sender=ValveState)
# def update_valve_states(sender, instance, **kwargs):
#     if not instance.pk:  # только для новых записей
#         # Закрываем все активные состояния для этой арматуры
#         ValveState.objects.filter(
#             valve=instance.valve,
#             timestamp__lt=instance.timestamp
#         ).update(is_current=False)
