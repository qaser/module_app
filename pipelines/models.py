import datetime as dt
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now

from equipments.models import Department, Equipment
from users.models import ModuleUser


class Pipeline(models.Model):
    title = models.CharField('Название газопровода', max_length=100)
    order = models.PositiveSmallIntegerField('Номер газопровода', default=1)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Газопровод'
        verbose_name_plural = 'Газопроводы'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return self.title


class Pipe(models.Model):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='pipes'
    )
    departments = models.ManyToManyField(
        Department,
        through='PipeDepartment',
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
    exploit_year = models.PositiveIntegerField(
        'Год ввода в эксплуатацию',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Участок газопровода'
        verbose_name_plural = 'Участки газопроводов'
        ordering = ['pipeline']
        indexes = [
            models.Index(fields=['pipeline']),
            models.Index(fields=['start_point', 'end_point']),
            models.Index(fields=['diameter']),
        ]

    @property
    def current_state(self):
        return self.states.filter(end_date__isnull=True).first()

    def __str__(self):
        return f'{self.start_point}-{self.end_point} км г-да "{self.pipeline}"'


class PipeDepartment(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        verbose_name='Участок газопровода',
        on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Филиал',
        on_delete=models.CASCADE
    )
    start_point = models.FloatField(
        verbose_name='Начало участка, км',
        blank=True,
        null=True
    )
    end_point = models.FloatField(
        verbose_name='Конец участка, км',
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('pipe', 'department')
        verbose_name = 'Эксплуатирующий филиал'
        verbose_name_plural = 'Эксплуатирующие филиалы'

    def save(self, *args, **kwargs):
        if not self.pk:  # Только при создании
            existing_count = PipeDepartment.objects.filter(pipe=self.pipe).count()
            if existing_count == 0:
                self.start_point = self.pipe.start_point
                self.end_point = self.pipe.end_point

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.pipe} — {self.department}'


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
    sub_pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='join_nodes',
        null=True,
        blank=True
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
    is_shared = models.BooleanField(
        verbose_name='Пограничный',
        default=False,
        blank=False,
        null=False,
        help_text='Расположен на участке совместной эксплуатации'
    )

    class Meta:
        verbose_name = 'Крановый узел'
        verbose_name_plural = 'Крановые узлы'
        ordering = ['pipeline']
        indexes = [
            models.Index(fields=['pipeline']),
            models.Index(fields=['equipment']),
            models.Index(fields=['node_type']),
            models.Index(fields=['location_point']),
        ]

    def clean(self):
        if self.node_type == 'bridge' and self.sub_pipeline is None:
            raise ValidationError(
                {'sub_pipeline': 'Для перемычки необходимо выбрать второй газопровод.'}
            )
        if self.node_type != 'bridge' and self.sub_pipeline is not None:
            raise ValidationError(
                {'sub_pipeline': 'Поле указывается только для перемычки.'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        departments = self.equipment.departments.all()
        root_department = None
        if departments.exists():
            root_department = departments.order_by('tree_id', 'level').first().get_root()
        department_name = root_department.name if root_department else '—'
        if self.node_type == 'bridge':
            return f'Перемычка {self.location_point} км между "{self.pipeline}" и "{self.sub_pipeline}"'
        else:
            node_type_display = self.get_node_type_display()
            return f'{node_type_display} {self.location_point} км г-да "{self.pipeline}"'

    # @property
    # def current_state(self):
    #     return self.states.filter('timestamp').first()


class Repair(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='pipe_repairs',
        null=True,
        blank=True
    )
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='node_repairs',
        null=True,
        blank=True
    )
    start_date = models.DateField(
        verbose_name='Начало ремонта',
        null=True,
        blank=True
    )
    end_date = models.DateField(
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
        verbose_name = 'Ремонт МГ, КУ'
        verbose_name_plural = 'Ремонты МГ, КУ'
        indexes = [
            models.Index(fields=['pipe']),
            models.Index(fields=['node']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def clean(self):
        super().clean()
        if not self.pipe and not self.node:
            raise ValidationError("Необходимо указать либо участок МГ, либо КУ.")
        if self.pipe and self.node:
            raise ValidationError("Нельзя указывать одновременно и участок ЛЧ, и КУ.")

    def save(self, *args, **kwargs):
        self.full_clean()  # обязательно вызывает clean()
        super().save(*args, **kwargs)


class RepairStage(models.Model):
    repair = models.ForeignKey(
        Repair,
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
        verbose_name = 'Документация по ремонту'
        verbose_name_plural = 'Документация по ремонтам'


class Diagnostics(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='pipe_diagnostics',
        blank=True,
        null=True,
    )
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='node_diagnostics',
        blank=True,
        null=True,
    )
    start_date = models.DateField(
        verbose_name='Начало ВТД',
        null=True,
        blank=True
    )
    end_date = models.DateField(
        verbose_name='Окончание ВТД',
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name='Дополнительная информация',
        max_length=500,
        blank=True
    )

    class Meta:
        verbose_name = 'ВТД'
        verbose_name_plural = 'ВТД'
        indexes = [
            models.Index(fields=['pipe']),
            models.Index(fields=['node']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def clean(self):
        super().clean()
        if not self.pipe and not self.node:
            raise ValidationError("Необходимо указать либо участок (pipe), либо узел (node).")
        if self.pipe and self.node:
            raise ValidationError("Нельзя указывать одновременно и участок (pipe), и узел (node).")

    def save(self, *args, **kwargs):
        self.full_clean()  # обязательно вызывает clean()
        super().save(*args, **kwargs)


class PipeState(models.Model):
    STATE_CHOICES = [
        ('repair', 'В ремонте'),
        ('operation', 'В работе'),
        ('disabled', 'Отключен'),
        # ('empty', 'Стравлен'),
        ('depletion', 'На выработке'),
        ('diagnostics', 'Проведение ВТД'),
    ]
    STATE_COLORS = {
        'repair': '#FF0000',  # Красный
        'operation': '#00FF00',  # Зеленый
        'disabled': '#888888',  # Серый
        # 'empty': '#FFFFFF',  # Белый
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
    start_date = models.DateField(
        verbose_name='Начало состояния',
        blank=False,
        null=False,
    )
    end_date = models.DateField(
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

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Состояние участка'
        verbose_name_plural = 'Состояния участков'
        indexes = [
            models.Index(fields=['pipe']),
            models.Index(fields=['state_type']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f'{self.get_state_type_display()} ({self.pipe})'

    @property
    def color(self):
        return self.STATE_COLORS.get(self.state_type, '#CCCCCC')

    # def clean(self):
    #     if self.end_date and self.end_date < self.start_date:
    #         raise ValidationError('Дата окончания не может быть раньше даты начала')

    def save(self, *args, **kwargs):
        PipeState.objects.filter(
            pipe=self.pipe,
            end_date__isnull=True
        ).exclude(pk=self.pk).update(end_date=self.start_date)
        super().save(*args, **kwargs)


class PipeLimit(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='limits'
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
    start_date = models.DateField(
        verbose_name='Начало ограничения',
        blank=False,
        null=False,
    )
    end_date = models.DateField(
        verbose_name='Окончание ограничения',
        null=True,
        blank=True,
        help_text='Указывается когда ограничение фактически будет снято'
    )

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Ограничение давления'
        verbose_name_plural = 'Ограничения давления'

    def __str__(self):
        return f'Ограничение {self.pressure_limit} кгс/см² ({self.pipe}) с {self.start_date}'

    def save(self, *args, **kwargs):
        # Закрываем предыдущие активные ограничения
        if self.start_date and self.pipe:
            PipeLimit.objects.filter(
                pipe=self.pipe,
                end_date__isnull=True
            ).exclude(pk=self.pk).update(end_date=self.start_date)
        self.full_clean()
        super().save(*args, **kwargs)


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
    state_type = models.CharField(
        max_length=25,
        choices=NODE_STATES,
        verbose_name='Состояние'
    )
    start_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата изменения'
    )
    end_date = models.DateField(
        verbose_name='Окончание состояния',
        null=True,
        blank=True
    )
    changed_by = models.ForeignKey(
        ModuleUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Кем изменено'
    )
    description = models.TextField(
        verbose_name='Комментарий',
        max_length=500,
        blank=True
    )

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Состояние кранового узла'
        verbose_name_plural = 'Состояния крановых узлов'
        indexes = [
            models.Index(fields=['node']),
            models.Index(fields=['state_type']),
            models.Index(fields=['start_date']),
            models.Index(fields=['changed_by']),
        ]

    def __str__(self):
        return f"{self.node} - {self.get_state_type_display()}"

    def save(self, *args, **kwargs):
        NodeState.objects.filter(
            node=self.node,
            end_date__isnull=True
        ).exclude(pk=self.pk).update(end_date=now().date())

        super().save(*args, **kwargs)


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
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['year']),
            models.Index(fields=['department', 'year']),
        ]

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
            raise ValidationError('Необходимо указать либо участок МГ, либо КУ.')
        if self.pipe and self.node:
            raise ValidationError('Нельзя одновременно указывать и участок МГ, и КУ.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        target = self.pipe or self.node
        return f"{self.get_work_type_display()} — {target} ({self.planned_date})"


class Tube(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='tubes'
    )
    tube_num = models.CharField("Номер трубы", max_length=20)
    active = models.BooleanField(default=True, verbose_name="Актуальная труба")
    installed_date = models.DateField("Дата установки", null=True, blank=True)
    removed_date = models.DateField("Дата удаления", null=True, blank=True)

    class Meta:
        verbose_name = "Труба (физическая)"
        verbose_name_plural = "Трубы (физические)"
        ordering = ["tube_num"]

    def __str__(self):
        return f"Труба №{self.tube_num} ({'активна' if self.active else 'удалена'})"


class TubeVersion(models.Model):
    TUBE_TYPE = [
        ('one', '1Ш'),
        ('two', '2Ш'),
        ('spiral', 'СШ'),
        ('without', 'БШ'),
    ]
    CATEGORY_CHOICES = [
        ('B', 'B'),
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
        ('IV', 'IV'),
    ]
    tube = models.ForeignKey(
        Tube,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    diagnostics = models.ForeignKey(
        "Diagnostics",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    repair = models.ForeignKey(
        "Repair",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date = models.DateField(null=True, blank=True)
    version_type = models.CharField(
        max_length=20,
        choices=[
            ("initial", "Первичное состояние"),
            ("diagnostic", "После диагностики"),
            ("repair", "После ремонта"),
        ],
    )
    tube_length = models.FloatField(
        'Длина трубы',
        null=False,
        blank=False,
    )
    thickness = models.FloatField(
        'Толщина трубы, мм',
        null=False,
        blank=False,
    )
    tube_type = models.CharField(
        max_length=50,
        choices=TUBE_TYPE,
        default='2Ш',
        verbose_name='Тип трубы',
        blank=False,
        null=False,
    )
    diameter = models.PositiveSmallIntegerField(
        'Диаметр трубы, мм',
        default=1420,
        null=False,
        blank=False,
    )
    yield_strength = models.PositiveSmallIntegerField(
        'Предел текучести стали, МПа',
        default=0,
        null=False,
        blank=False,
    )
    tear_strength = models.PositiveSmallIntegerField(
        'Сопротивление разрыву стали, МПа',
        default=0,
        null=False,
        blank=False,
    )
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='II',
        verbose_name='Категория трубы',
        blank=False,
        null=False,
    )
    reliability_material = models.FloatField(
        'Коэффициент надёжности по материалу',
        null=True,
        blank=True,
        help_text='Согласно СНиП 2.05.06-85'
    )
    working_conditions = models.FloatField(
        'Коэффициент условий работы трубопровода',
        null=True,
        blank=True,
        help_text='Согласно СНиП 2.05.06-85'
    )
    reliability_pressure = models.FloatField(
        'Коэффициент надёжности по внутреннему рабочему давлению',
        null=True,
        blank=True,
        help_text='Согласно СНиП 2.05.06-85'
    )
    reliability_coef = models.FloatField(
        'Коэффициент надёжности трубопровода',
        null=True,
        blank=True,
        help_text='Согласно СНиП 2.05.06-85'
    )
    impact_strength = models.FloatField(
        'Ударная вязкость стали, Дж/см²',
        null=True,
        blank=True
    )
    steel_grade = models.CharField(
        'Марка стали',
        max_length=50,
        null=True,
        blank=True
    )
    weld_position = models.CharField(
        'Положение швов, час',
        max_length=100,
        null=True,
        blank=True,
        help_text='Формат: "2.3 = 8.3" для двухшовных, "2.3 // 11.5" для спиральных, "-" для бесшовных'
    )
    # Реперные точки
    from_reference_start = models.CharField(
        verbose_name='От репера, м',
        max_length=50,
        blank=True,
        null=True,
    )
    to_reference_end = models.CharField(
        verbose_name='До репера, м',
        max_length=50,
        blank=True,
        null=True,
    )
    comment = models.TextField(
        'Комментарий',
        null=True,
        blank=True,
        help_text='Любой значимый комментарий для данной трубы'
    )

    class Meta:
        verbose_name = 'Труба'
        verbose_name_plural = 'Трубы'
        # ordering = ['tube_num']

    # def __str__(self):
    #     return f'Труба №{self.tube_num}, участок {self.pipe}'


class TubeUnit(models.Model):
    UNIT_TYPE = [
        ('valv', 'Кран'),
        ('offt', 'Отвод-врезка'),
        ('tee', 'Тройник'),
        ('cpco', 'Подключение системы ЭХЗ'),
        ('wiwd', 'Заварка окна'),
        ('casb', 'Футляр-начало'),
        ('case', 'Футляр-конец'),
        ('mark', 'Маркер'),
        ('anch', 'Пригруз'),
        ('pfix', 'Элемент обустройства'),
    ]
    unit_type = models.CharField(
        max_length=50,
        choices=UNIT_TYPE,
        verbose_name='Тип элемента',
        blank=False,
        null=False,
    )
    tube = models.ForeignKey(
        Tube,
        on_delete=models.CASCADE,
        related_name='tube_units',
        blank=True,
        null=True,
    )
    comment = models.TextField(
        'Комментарий',
        null=True,
        blank=True,
        help_text='Любой значимый комментарий для данного элемента'
    )

    class Meta:
        verbose_name = 'Элемент обустройства'
        verbose_name_plural = 'Элементы обустройства'

    def __str__(self):
        return f'{self.unit_type}, {self.tube}'


class Anomaly(models.Model):
    ANOMALY_NATURE = [
        ('gwan', 'Аномалия кольцевого шва'),
        ('lwan', 'Аномалия продольного шва'),
        ('goug', 'Механическое повреждение'),
        ('corr', 'Коррозия'),
        ('dent', 'Вмятина'),
        ('wrin', 'Гофр'),
        ('artd', 'Технологический дефект'),
        ('mian', 'Заводской дефект'),
        ('scc', 'Зона продольных трещин'),
        ('lwcr', 'Трещина на продольном шве'),
    ]
    SIZE_CLASS = [
        ('', 'Не указан'),
        ('gene', 'Обширный'),
        ('pitt', 'Каверна'),
        ('cigr', 'Поперечная канавка'),
        ('axgr', 'Продольная канавка'),
        ('axsl', 'Продольный паз'),
        ('cisl', 'Поперечный паз'),
    ]
    LOCATION = [
        ('int', 'INT'),
        ('ext', 'EXT'),
        ('mid', 'MID'),
        ('n/a', 'N/A'),
    ]

    diagnostics = models.ForeignKey(
        Diagnostics,
        on_delete=models.CASCADE,
        related_name='diagnostics_anomalies'
    )
    tube = models.ForeignKey(
        TubeVersion,
        on_delete=models.CASCADE,
        related_name='anomalies',
        blank=False,
        null=False,
    )
    distance = models.FloatField(
        verbose_name='Расстояние, м',
        blank=True,
        null=True,
    )
    # Геометрические параметры
    from_left_weld_to_max = models.FloatField(
        verbose_name='От левого шва до точки максимума, м',
        blank=True,
        null=True,
    )
    from_left_weld_to_start = models.FloatField(
        verbose_name='От левого шва до начала, м',
        blank=True,
        null=True,
    )
    from_right_weld_to_max = models.FloatField(
        verbose_name='От правого шва до точки максимума, м',
        blank=True,
        null=True,
    )
    from_right_weld_to_start = models.FloatField(
        verbose_name='От правого шва до начала, м',
        blank=True,
        null=True,
    )
    # Ориентационные параметры
    from_long_weld_to_start = models.IntegerField(
        verbose_name='От продольного шва до точки начала дефекта, мм',
        blank=True,
        null=True,
    )
    from_long_weld_to_max = models.IntegerField(
        verbose_name='От продольного шва до точки максимума, мм',
        blank=True,
        null=True,
    )
    from_long_weld_to_center = models.IntegerField(
        verbose_name='От продольного шва до центра, мм',
        blank=True,
        null=True,
    )
    min_distance_to_long_weld = models.IntegerField(
        verbose_name='Минимальное расстояние до продольного шва, мм',
        blank=True,
        null=True,
    )
    min_distance_to_circ_weld = models.IntegerField(
        verbose_name='Минимальное расстояние до кольцевого шва, мм',
        blank=True,
        null=True,
    )
    start_point_orientation = models.CharField(
        verbose_name='Ориентация точки начала дефекта, ч:мин',
        max_length=5,
        blank=True,
        null=True,
    )
    max_point_orientation = models.CharField(
        verbose_name='Ориентация точки максимума, ч:мин',
        max_length=5,
        blank=True,
        null=True,
    )
    center_orientation = models.CharField(
        verbose_name='Ориентация центра, ч:мин',
        max_length=5,
        blank=True,
        null=True,
    )
    # Характеристики аномалии
    anomaly_nature = models.CharField(
        max_length=50,
        choices=ANOMALY_NATURE,
        verbose_name='Характер аномалии',
        blank=True,
        null=True,
    )
    anomaly_description = models.CharField(
        verbose_name='Описание',
        max_length=200,
        blank=True,
        null=True,
    )
    size_class = models.CharField(
        max_length=50,
        choices=SIZE_CLASS,
        verbose_name='Класс размера',
        blank=True,
        null=True,
    )
    # Геометрические размеры
    anomaly_length = models.PositiveSmallIntegerField(
        verbose_name='Длина аномалии, мм',
        default=0,
        blank=False,
        null=False,
    )
    anomaly_width = models.PositiveSmallIntegerField(
        verbose_name='Ширина аномалии, мм',
        default=0,
        blank=False,
        null=False,
    )
    anomaly_depth = models.PositiveSmallIntegerField(
        verbose_name='Глубина аномалии, %',
        default=0,
        blank=False,
        null=False,
    )
    location = models.CharField(
        max_length=10,
        choices=LOCATION,
        verbose_name='Расположение',
        blank=True,
        null=True,
    )
    danger_level = models.CharField(
        verbose_name='Опасность',
        max_length=10,
        blank=True,
        null=True,
    )
    # Комментарии
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Аномалия'
        verbose_name_plural = 'Аномалии'
        indexes = [
            models.Index(fields=['diagnostics']),
            models.Index(fields=['tube']),
            models.Index(fields=['anomaly_nature']),
        ]
        # ordering = ['tube__tube_num',]

    def __str__(self):
        return f'Аномалия на трубе №{self.tube.tube_num if self.tube else "N/A"}'


class Defect(models.Model):
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
    anomaly = models.OneToOneField(
        Anomaly,
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
    description = models.TextField(
        verbose_name='Дополнительная информация',
        max_length=500,
        blank=True
    )

    class Meta:
        verbose_name = 'Дефект'
        verbose_name_plural = 'Дефекты'
        indexes = [
            models.Index(fields=['defect_type']),
        ]


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
        related_name='hole_docs'
    )
    doc = models.FileField(upload_to='pipelines/docs/holes/')
    name = models.CharField(
        'Наименование документа',
        max_length=100,
        blank=False,
        null=False,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Документация по ТО'
        verbose_name_plural = 'Документация по ТО'


class PipeDocument(models.Model):
    pipe = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='pipe_docs'
    )
    doc = models.FileField(upload_to='pipelines/docs/pipes/')
    name = models.CharField(
        'Наименование документа',
        max_length=100,
        blank=False,
        null=False,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Документация участка МГ'
        verbose_name_plural = 'Документация участков МГ'


class NodeDocument(models.Model):
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='node_docs'
    )
    doc = models.FileField(upload_to='pipelines/docs/nodes/')
    name = models.CharField(
        'Наименование документа',
        max_length=100,
        blank=False,
        null=False,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Документация КУ МГ'
        verbose_name_plural = 'Документация КУ МГ'


class RepairDocument(models.Model):
    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name='repair_docs'
    )
    doc = models.FileField(upload_to='pipelines/docs/repairs/')
    name = models.CharField(
        'Наименование документа',
        max_length=100,
        blank=False,
        null=False,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Документация по ремонту участка МГ'
        verbose_name_plural = 'Документация по ремонтам участков МГ'
