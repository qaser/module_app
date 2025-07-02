import datetime as dt
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

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
        ordering = ['pipeline']

    @property
    def current_state(self):
        return self.states.filter(end_date__isnull=True).first()

    def __str__(self):
        return f'{self.department} "{self.pipeline}" {self.start_point}-{self.end_point} км'


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

    class Meta:
        verbose_name = 'Ремонт участка МГ'
        verbose_name_plural = 'Ремонты участков МГ'


class PipeRepairDocument(models.Model):
    repair = models.ForeignKey(
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
    event_date = models.DateTimeField(
        verbose_name='Дата проведения',
        blank=False,
        null=False,
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

    class Meta:
        verbose_name = 'Документация по ремонту участка МГ'
        verbose_name_plural = 'Документация по ремонтам участков МГ'


class PipeDiagrostics(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='diagnostics'
    )
    event_date = models.DateTimeField(
        verbose_name='Дата проведения ВТД',
        blank=False,
        null=False,
    )
    description = models.TextField(
        verbose_name='Дополнительная информация',
        max_length=500,
        blank=True
    )

    class Meta:
        verbose_name = 'ВТД участка МГ'
        verbose_name_plural = 'ВТД участков МГ'


class Defect(models.Model):
    DEFECT_PLACE = [
        ('tube', 'Труба'),
        ('kss', 'КСС'),
        ('sdt', 'СДТ'),
    ]
    DEFECT_TYPE = [
        ('krn', 'КРН'),
        ('scratch', 'Царапина'),
        ('burr', 'Задир'),
        ('dent', 'Вмятина'),
        ('crack', 'Трещина'),
        ('shell', 'Раковина'),
        ('potholes', 'Забоина'),
        ('risk', 'Риска'),
        ('oval', 'Овальность'),
        ('curve', 'Кривизна'),
        ('goffer', 'Гофр'),
        ('notbrewed', 'Непровар'),
        ('undercutting', 'Подрез зоны сплавления'),
        ('displacement', 'Смещение сваренных кромок'),
        ('pore', 'Пора'),
        ('slag', 'Шлаковые включения'),
        ('fistula', 'Свищ в сварном шве'),
    ]
    diagnostics = models.ForeignKey(
        PipeDiagrostics,
        on_delete=models.CASCADE,
        related_name='defects'
    )
    defect_num = models.PositiveSmallIntegerField(
        verbose_name='Номер дефекта',
        blank=False,
        null=False,
    )
    defect_type = models.CharField(
        max_length=50,
        choices=DEFECT_TYPE,
        verbose_name='Тип дефекта',
        blank=False,
        null=False,
    )
    defect_place = models.CharField(
        max_length=50,
        choices=DEFECT_PLACE,
        verbose_name='Место расположения дефекта',
        blank=False,
        null=False,
    )
    place_num = models.CharField(
        verbose_name='Номер трубы (КСС, СДТ)',
        blank=True,
        null=True,
    )
    is_fixed = models.BooleanField(
        verbose_name='Дефект устранён',
        default=False
    )
    description = models.TextField(
        verbose_name='Дополнительная информация',
        max_length=500,
        blank=True
    )

    class Meta:
        verbose_name = 'Дефект трубопровода (КСС, СДТ)'
        verbose_name_plural = 'Дефекты трубопроводов (КСС, СДТ)'

    def clean(self):
        super().clean()
        # Список допустимых типов дефектов для КСС
        kss_allowed_defects = [
            'notbrewed',
            'undercutting',
            'displacement',
            'pore',
            'slag',
            'crack',
            'shell',
            'fistula',
        ]
        if self.defect_place == 'kss' and self.defect_type not in kss_allowed_defects:
            raise ValidationError(
                ("Для места расположения 'КСС' допустимы только следующие типы дефектов: "
                 ', '.join([dict(self.DEFECT_TYPE)[d] for d in kss_allowed_defects]))
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
    cutting_date = models.DateField(
        verbose_name='Дата вырезки',
        null=False,
        blank=False,
    )
    welding_date = models.DateField(
        verbose_name='Дата заварки',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Технологическое отверстие'
        verbose_name_plural = 'Технологические отверстия'


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
        max_length=25,
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
        verbose_name='Давление, кгс/см²',
        null=True,
        blank=True
    )
    pressure_limit = models.FloatField(
        verbose_name='Ограничение давления, кгс/см²',
        null=True,
        blank=True
    )
    limit_reason = models.CharField(
        max_length=100,
        verbose_name='Причина ограничения',
        null=True,
        blank=True
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
        ('tails', 'Шлейфы'),
        ('ks', 'КС'),
    ]
    TYPE_ORIENTATION = [
        ('normal', 'Нормально'),
        ('reverse', 'Реверсивно'),
    ]
    node_type = models.CharField(
        max_length=25,
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
    orientation = models.CharField(
        max_length=40,
        choices=TYPE_ORIENTATION,
        verbose_name='Ориентация',
        help_text='Как элемент расположен на схеме',
        default='normal',
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Крановый узел'
        verbose_name_plural = 'Крановые узлы'
        ordering = ['pipeline']

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
        max_length=25,
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


class ComplexPlan(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='pipelines_plans',
        verbose_name='Филиал'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год планирования',
        choices=[(y, y) for y in range(datetime.now().year, datetime.now().year + 4)]
    )

    class Meta:
        unique_together = ('department', 'year')
        verbose_name = 'КПГ'
        verbose_name_plural = 'КПГ'

    def __str__(self):
        return f'КПГ {self.year}г. - {self.department.name}'


class PlannedWork(models.Model):
    WORK_TYPE_CHOICES = [
        ('repair', 'Ремонт'),
        ('replacement', 'Замена'),
        ('diagnostics', 'ВТД'),
    ]
    complex_plan = models.ForeignKey(
        ComplexPlan,
        on_delete=models.CASCADE,
        related_name='planned_works',
        verbose_name='КПГ'
    )
    work_type = models.CharField(
        max_length=50,
        choices=WORK_TYPE_CHOICES,
        verbose_name='Тип работы'
    )
    description = models.TextField(
        verbose_name='Описание работы',
        blank=True,
    )
    start_date = models.DateField(
        verbose_name='Плановая дата начала'
    )
    end_date = models.DateField(
        verbose_name='Плановая дата окончания'
    )
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='planned_works',
        verbose_name='Участок газопровода'
    )
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='planned_works',
        verbose_name='Крановый узел'
    )

    class Meta:
        verbose_name = 'Запланированная работа'
        verbose_name_plural = 'Запланированные работы'
        ordering = ['complex_plan']

    def clean(self):
        if not self.pipe and not self.node:
            raise ValidationError('Необходимо указать либо участок газопровода, либо крановый узел.')
        if self.pipe and self.node:
            raise ValidationError('Нельзя одновременно указывать и участок газопровода, и крановый узел.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        target = self.pipe or self.node
        return f"{self.get_work_type_display()} — {target} ({self.planned_date})"


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
