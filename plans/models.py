import calendar
import datetime as dt

from dateutil.relativedelta import relativedelta
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.utils import timezone

from equipments.models import Department
from users.models import ModuleUser


class EventStatus:
    """Общий класс для статусов мероприятий"""
    NOT_STARTED = 'not_started'
    IN_WORK = 'in_work'
    DEADLINE = 'deadline'
    OVERDUE = 'overdue'
    DELAYED = 'delayed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    CHOICES = [
        (NOT_STARTED, 'Не начато'),
        (IN_WORK, 'В работе'),
        (DEADLINE, 'Подходит срок исполнения'),
        (OVERDUE, 'Истёк срок исполнения'),
        (DELAYED, 'Задержка'),
        (COMPLETED, 'Выполнено'),
        (CANCELLED, 'Отменено'),
    ]

    ACTIVE_STATUSES = [NOT_STARTED, IN_WORK, DEADLINE, DELAYED]
    FINAL_STATUSES = [COMPLETED, CANCELLED]
    PROBLEM_STATUSES = [OVERDUE, DELAYED]

    @classmethod
    def get_display_name(cls, status):
        """Получить отображаемое название статуса"""
        return dict(cls.CHOICES).get(status, status)


class Document(models.Model):
    CATEGORY_CHOICES = [
        ("order", 'Приказ'),
        ("protocol", 'Протокол'),
        ("ordinance", 'Распоряжение'),
        ("report", 'Отчёт'),
        ("inspect", 'Акт проверки'),
    ]
    category = models.CharField(
        'Категория',
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="order",
    )
    title = models.CharField(
        'Наименование',
        max_length=500,
        blank=False,
        null=False,
    )
    num_doc = models.CharField(
        'Номер',
        max_length=20,
        blank=True,
        null=True,
    )
    date_doc = models.DateField(
        'Дата выхода',
        blank=True,
        null=True,
    )
    subject = models.CharField(
        'Направление',
        max_length=50,
        default='Общие вопросы',
        blank=False,
        null=False,
    )
    is_complete = models.BooleanField(
        'Все мероприятия выполнены',
        default=False
    )
    is_archived = models.BooleanField(
        'Архивирован',
        default=False,
    )

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    @property
    def full_title(self):
        if self.date_doc and self.num_doc:
            formatted_date = self.date_doc.strftime("%d.%m.%Y")
            return f'{self.get_category_display()} №{self.num_doc} от {formatted_date}г. "{self.title}"'
        else:
            return f'{self.get_category_display()} "{self.title}"'

    def __str__(self) -> str:
        return self.title[:30] + "..."


# === Event — шаблон мероприятия ===
class Event(models.Model):
    SCHEDULE_TYPE_CHOICES = [
        ('continuous', 'Постоянно'),
        ('once', 'Фиксированная дата'),
        ('periodic', 'Периодическое'),
    ]
    PERIOD_UNIT_CHOICES = [
        ('day', 'День'),
        ('week', 'Неделя'),
        ('month', 'Месяц'),
        ('quarter', 'Квартал'),
        ('year', 'Год'),
    ]
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='events'
    )
    owner = models.ForeignKey(
        ModuleUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events'
    )
    description = models.TextField('Содержание мероприятия', max_length=1000)
    departments = models.ManyToManyField(Department, related_name='events')
    schedule_type = models.CharField(
        'Тип расписания',
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        default='once'
    )
    # === periodic ===
    period_unit = models.CharField(
        'Единица периода',
        max_length=10,
        choices=PERIOD_UNIT_CHOICES,
        null=True,
        blank=True,
        help_text='Используется только для periodic'
    )
    period_interval = models.PositiveSmallIntegerField(
        'Интервал',
        default=1,
        null=True,
        blank=True,
        help_text='Каждые N периодов; используется только для periodic'
    )
    start_date = models.DateField(
        'Дата начала периода',
        null=True,
        blank=True,
        help_text='С какой даты начинать отсчёт периода'
    )
    due_date = models.DateField(
        'Дата исполнения',
        null=True,
        blank=True,
        help_text='Для фиксированной даты'
    )
    is_archived = models.BooleanField('Архивировано', default=False)

    class Meta:
        verbose_name = 'Шаблон мероприятие'
        verbose_name_plural = 'Шаблоны мероприятий'

    def __str__(self):
        return self.description[:50]


# === EventInstance — конкретная дата исполнения мероприятия ===
class EventInstance(models.Model):
    _allow_status_update = False
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='instances'
    )
    due_date = models.DateField(
        'Срок выполнения',
        null=True,
        blank=True
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=EventStatus.CHOICES,
        default=EventStatus.NOT_STARTED
    )
    completed_at = models.DateField(
        'Фактическая дата выполнения',
        null=True,
        blank=True
    )
    is_archived = models.BooleanField('Архивировано', default=False)

    @property
    def days_until_due(self):
        """
        Количество дней до срока исполнения.
        < 0 — просрочено
        0..3 — подходит срок
        None — срок не задан
        """
        if not self.due_date:
            return None
        today = timezone.now().date()
        return (self.due_date - today).days

    @property
    def computed_status(self):
        """
        Статус с учётом дедлайна
        """
        if self.status == EventStatus.COMPLETED:
            return EventStatus.COMPLETED
        days = self.days_until_due
        if days is None:
            return self.status
        if days < 0:
            return EventStatus.OVERDUE
        if (
            self.status in (
                EventStatus.NOT_STARTED,
                EventStatus.IN_WORK,
            )
            and days <= 3
        ):
            return EventStatus.DEADLINE
        return self.status

    @property
    def computed_status_display(self):
        return EventStatus.get_display_name(self.computed_status)

    @property
    def status_css_class(self):
        return {
            'completed': 'event-card--status-completed',
            'overdue': 'event-card--status-overdue',
            'deadline': 'event-card--status-deadline',
            'not_started': 'event-card--status-not_started',
            'in_work': 'event-card--status-in_work',
            'delayed': 'event-card--status-delayed',
            'cancelled': 'event-card--status-cancelled',
        }.get(self.computed_status, 'event-card--status-not_started')

    class Meta:
        verbose_name = 'Экземпляр мероприятия'
        verbose_name_plural = 'Экземпляры мероприятий'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.event} — {self.due_date} — {self.status}"

    def set_status(self, status, *, completed_at=None):
        self._allow_status_update = True
        self.status = status
        if completed_at:
            self.completed_at = completed_at
        self.save(update_fields=['status', 'completed_at'])
        self._allow_status_update = False


# === EventCompletion — выполнение мероприятия подразделением ===
class EventCompletion(models.Model):
    """
    Выполнение мероприятия конкретным подразделением для конкретного instance.
    """
    instance = models.ForeignKey(
        EventInstance,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='event_completions'
    )
    status = models.CharField(
        'Статус выполнения',
        max_length=20,
        choices=EventStatus.CHOICES,
        default=EventStatus.NOT_STARTED
    )
    actual_completion_date = models.DateField(
        'Фактическая дата выполнения',
        null=True,
        blank=True
    )
    comment = models.TextField('Комментарий / отчёт', null=True, blank=True, max_length=1000)
    assigned_by = models.ForeignKey(
        ModuleUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_event_completions'
    )
    assigned_at = models.DateTimeField('Дата отметки', default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Выполнение мероприятия'
        verbose_name_plural = 'Выполнения мероприятий'
        indexes = [
            models.Index(fields=['instance', 'status']),
            models.Index(fields=['department', 'status']),
        ]
        unique_together = ('instance', 'department')

    def __str__(self):
        return f'{self.department} — {self.instance}'

    def clean(self):
        """
        Валидация: department должен входить в event.departments
        """
        if self.department and self.instance:
            if not self.instance.event.departments.filter(id=self.department.id).exists():
                raise ValidationError({
                    'department': f'Подразделение "{self.department}" не относится к мероприятию "{self.instance.event}".'
                })







class Protocol(models.Model):
    title = models.CharField(
        'Наименование протокола',
        max_length=500,
        blank=False,
        null=False,
    )
    subject = models.CharField(
        'Направление',
        max_length=50,
        blank=False,
        null=False,
    )
    num_protocol = models.CharField(
        'Номер протокола',
        max_length=20,
        blank=False,
        null=False,
    )
    date_protocol = models.DateField(
        'Дата совещания',
        blank=False,
        null=False,
    )
    is_complete = models.BooleanField(
        'Все мероприятия выполнены',
        default=False
    )
    is_archive = models.BooleanField(
        'Архивирован',
        default=False
    )

    class Meta:
        verbose_name = 'Протокол'
        verbose_name_plural = 'Протоколы'

    @property
    def full_title(self):
        formatted_date = self.date_protocol.strftime("%d.%m.%Y")
        return f'Протокол №{self.num_protocol} от {formatted_date}г. "{self.title}"'

    def __str__(self) -> str:
        formatted_date = self.date_protocol.strftime("%d.%m.%Y")
        title_length = len(self.title)
        if title_length > 20:
            truncated_title = self.title[:20] + "..."
        else:
            truncated_title = self.title
        return (
            f"Протокол №{self.num_protocol} от {formatted_date}г. "
            f"{truncated_title}"
        )


class ProtocolActivity(models.Model):
    STATUS_CHOICES = [
        ("open", 'В работе'),
        ("approaching_deadline", 'Подходит срок исполнения'),
        ("overdue", 'Истёк срок исполнения'),
        ("completed", 'Выполнено'),
    ]
    DEADLINE_TYPES = [
        ("date", "Фиксированная дата"),
        # ("periodic", "Периодически"),
        ("permanent", "Постоянно"),
    ]
    protocol = models.ForeignKey(
        'Protocol',
        verbose_name='Протокол',
        related_name='activities',
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        'Содержание мероприятия',
        max_length=1000,
        blank=False,
        null=False,
    )
    deadline_type = models.CharField(
        'Тип срока исполнения',
        max_length=20,
        choices=DEADLINE_TYPES,
        default="date",
    )
    deadline_date = models.DateField(
        'Срок исполнения',
        blank=True,
        null=True,
        help_text='Укажите дату окончания срока (для разовых задач).'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )
    actual_completion_date = models.DateField(
        'Дата фактического завершения',
        blank=True,
        null=True,
        help_text='Дата фактического завершения мероприятия.'
    )
    last_status_check = models.DateTimeField(
        'Последняя проверка статуса',
        auto_now=True,
        help_text='Автоматически обновляется при изменении или проверке.'
    )
    departments = models.ManyToManyField(
        Department,
        verbose_name='Подразделения',
        related_name='protocol_activities',
        blank=False,
    )
    is_archived = models.BooleanField(
        'Архивировано',
        default=False
    )

    class Meta:
        verbose_name = 'Мероприятие протокола'
        verbose_name_plural = 'Мероприятия протокола'
        indexes = [
            models.Index(fields=['protocol']),
            models.Index(fields=['status']),
            models.Index(fields=['deadline_date']),
            models.Index(fields=['deadline_type']),
        ]

    def __str__(self) -> str:
        return self.description


class ProtocolActivityResponsibility(models.Model):
    activity = models.ForeignKey(
        ProtocolActivity,
        verbose_name='Мероприятие',
        related_name='responsibilities',
        on_delete=models.CASCADE,
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Подразделение',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        'Статус исполнения',
        max_length=20,
        choices=[
            ("open", 'В работе'),
            ("mark", 'Отмечено'),  # для периодических и постоянных мероприятий
            ("completed", 'Выполнено'),
        ],
        default="open",
    )
    actual_completion_date = models.DateField(
        'Дата фактического завершения',
        blank=True,
        null=True,
        help_text='Когда подразделение фактически завершило задачу.'
    )
    comment = models.TextField(
        'Комментарий',
        blank=True,
        null=True,
        max_length=100,
        help_text='Дополнительная информация от подразделения.'
    )
    updated_at = models.DateTimeField(
        'Последнее обновление',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Выполнение мероприятий протоколов'
        verbose_name_plural = 'Выполнение мероприятий протоколов'
        unique_together = ('activity', 'department')  # Одно подразделение — одна ответственность за мероприятие
        indexes = [
            models.Index(fields=['activity', 'department']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        super().clean()
        if self.activity and self.department:
            if not self.activity.departments.filter(id=self.department.id).exists():
                raise ValidationError({
                    'department': f'Подразделение "{self.department}" не входит в список подразделений мероприятия.'
                })
        if self.activity and self.status == 'completed' and self.activity.deadline_type != 'date':
            raise ValidationError({
                'status': 'Нельзя использовать статус "Выполнено" для мероприятий с типом "периодически" или "постоянно".'
            })

    def __str__(self):
        return f"{self.department} — {self.get_status_display()} ({self.activity})"


class Order(models.Model):
    title = models.CharField(
        'Наименование приказа',
        max_length=500,
        blank=False,
        null=False,
    )
    num_order = models.CharField(
        'Номер приказа',
        max_length=20,
        blank=False,
        null=False,
    )
    date_order = models.DateField(
        'Дата выхода',
        blank=False,
        null=False,
    )
    subject = models.CharField(
        'Направление',
        max_length=50,
        default='Общие вопросы',
        blank=False,
        null=False,
    )
    is_complete = models.BooleanField(
        'Все мероприятия выполнены',
        default=False
    )
    is_archive = models.BooleanField(
        'Архивирован',
        default=False
    )

    class Meta:
        verbose_name = 'Приказ'
        verbose_name_plural = 'Приказы'

    @property
    def full_title(self):
        formatted_date = self.date_order.strftime("%d.%m.%Y")
        return f'Приказ №{self.num_order} от {formatted_date}г. "{self.title}"'

    def __str__(self) -> str:
        formatted_date = self.date_order.strftime("%d.%m.%Y")
        title_length = len(self.title)
        if title_length > 20:
            truncated_title = self.title[:20] + "..."
        else:
            truncated_title = self.title
        return (
            f"Приказ №{self.num_order} от {formatted_date}г. "
            f"{truncated_title}"
        )


class OrderActivity(models.Model):
    STATUS_CHOICES = [
        ("open", 'В работе'),
        ("approaching_deadline", 'Подходит срок исполнения'),
        ("overdue", 'Истёк срок исполнения'),
        ("completed", 'Выполнено'),
    ]
    DEADLINE_TYPES = [
        ("date", "Фиксированная дата"),
        ("permanent", "Постоянно"),
    ]
    order = models.ForeignKey(
        'Order',
        verbose_name='Приказ',
        related_name='activities',
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        'Содержание мероприятия',
        max_length=1000,
        blank=False,
        null=False,
    )
    deadline_type = models.CharField(
        'Тип срока исполнения',
        max_length=20,
        choices=DEADLINE_TYPES,
        default="date",
    )
    deadline_date = models.DateField(
        'Срок исполнения',
        blank=True,
        null=True,
        help_text='Укажите дату окончания срока (для разовых задач).'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )
    actual_completion_date = models.DateField(
        'Дата фактического завершения',
        blank=True,
        null=True,
        help_text='Дата фактического завершения мероприятия.'
    )
    last_status_check = models.DateTimeField(
        'Последняя проверка статуса',
        auto_now=True,
        help_text='Автоматически обновляется при изменении или проверке.'
    )
    departments = models.ManyToManyField(
        Department,
        verbose_name='Подразделения',
        related_name='order_activities',
        blank=False,
    )
    is_archived = models.BooleanField(
        'Архивировано',
        default=False
    )

    class Meta:
        verbose_name = 'Мероприятие приказа'
        verbose_name_plural = 'Мероприятия приказов'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['deadline_date']),
            models.Index(fields=['deadline_type']),
        ]

    def __str__(self) -> str:
        return self.description


class OrderActivityResponsibility(models.Model):
    activity = models.ForeignKey(
        OrderActivity,
        verbose_name='Мероприятие',
        related_name='responsibilities',
        on_delete=models.CASCADE,
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Подразделение',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        'Статус исполнения',
        max_length=20,
        choices=[
            ("open", 'В работе'),
            ("mark", 'Отмечено'),  # для периодических и постоянных мероприятий
            ("completed", 'Выполнено'),
        ],
        default="open",
    )
    actual_completion_date = models.DateField(
        'Дата фактического завершения',
        blank=True,
        null=True,
        help_text='Когда подразделение фактически завершило задачу'
    )
    comment = models.TextField(
        'Комментарий',
        blank=True,
        null=True,
        max_length=100,
        help_text='Дополнительная информация от подразделения'
    )
    updated_at = models.DateTimeField(
        'Последнее обновление',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Выполнение мероприятий приказов'
        verbose_name_plural = 'Выполнение мероприятий приказов'
        unique_together = ('activity', 'department')  # Одно подразделение — одна ответственность за мероприятие
        indexes = [
            models.Index(fields=['activity', 'department']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        super().clean()
        if self.activity and self.department:
            if not self.activity.departments.filter(id=self.department.id).exists():
                raise ValidationError({
                    'department': f'Подразделение "{self.department}" не входит в список подразделений мероприятия.'
                })
        if self.activity and self.status == 'completed' and self.activity.deadline_type != 'date':
            raise ValidationError({
                'status': 'Нельзя использовать статус "Выполнено" для мероприятий с типом "периодически" или "постоянно".'
            })

    def __str__(self):
        return f"{self.department} — {self.get_status_display()} ({self.activity})"


class Report(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Единоразово'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('quarterly', 'Ежеквартально'),
        ('yearly', 'Ежегодно'),
        ('continuous', 'Постоянно'),
        ('custom', 'Особая периодичность'),
    ]
    STATUS_CHOICES = [
        ("open", 'В работе'),
        ("approaching_deadline", 'Подходит срок исполнения'),
        ("overdue", 'Истёк срок исполнения'),
        ("completed", 'Выполнено'),
    ]
    name = models.TextField(
        verbose_name='Название отчета',
        blank=False,
        null=False
    )
    departments = models.ManyToManyField(
        Department,
        verbose_name='Подразделения',
        related_name='reports',
        blank=False,
    )
    frequency = models.CharField(
        verbose_name='Периодичность',
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='once'
    )
    custom_frequency_description = models.TextField(
        verbose_name='Описание периодичности',
        blank=True,
        null=True
    )
    order_number = models.CharField(
        verbose_name='№ приказа',
        max_length=100,
        blank=True,
        null=True
    )
    order_date = models.DateField(
        verbose_name='Дата приказа',
        blank=True,
        null=True
    )
    address = models.TextField(
        verbose_name='Адресат',
        blank=True,
        null=True
    )
    comments = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        verbose_name='Активный',
        default=True
    )

    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'

    def __str__(self):
        return f'{self.name[:50]}...'


class ReportSchedule(models.Model):
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Отчет'
    )
    # Для еженедельных отчетов
    day_of_week = models.IntegerField(
        verbose_name='День недели (0-6, где 0 - понедельник)',
        blank=True,
        null=True,
        choices=[(i, day) for i, day in enumerate(['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'])]
    )
    # Для ежемесячных отчетов
    day_of_month = models.IntegerField(
        verbose_name='День месяца (1-31)',
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    # Для ежеквартальных отчетов
    quarter_month = models.IntegerField(
        verbose_name='Месяц квартала (1, 4, 7, 10)',
        blank=True,
        null=True,
        choices=[(1, 'Январь'), (4, 'Апрель'), (7, 'Июль'), (10, 'Октябрь')]
    )
    # Для ежегодных отчетов
    month_of_year = models.IntegerField(
        verbose_name='Месяц года',
        blank=True,
        null=True,
        choices=[(i, month) for i, month in enumerate(['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                                                     'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'], 1)]
    )
    # Для специальных случаев (например, "до 3 числа месяца")
    days_before_end_of_month = models.IntegerField(
        verbose_name='Дней до конца месяца',
        blank=True,
        null=True
    )
    # Для случаев "в течение N рабочих дней после события"
    days_after_trigger = models.IntegerField(
        verbose_name='Рабочих дней после триггера',
        blank=True,
        null=True
    )
    class Meta:
        verbose_name = 'Расписание отчета'
        verbose_name_plural = 'Расписания отчетов'


class ReportStatus(models.Model):
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='statuses',
        verbose_name='Отчет'
    )
    period_start = models.DateField(
        verbose_name='Начало отчетного периода'
    )
    period_end = models.DateField(
        verbose_name='Конец отчетного периода',
        blank=True,
        null=True
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=20,
        choices=Report.STATUS_CHOICES,
        default='pending'
    )
    due_date = models.DateField(
        verbose_name='Срок сдачи'
    )
    completed_date = models.DateField(
        verbose_name='Дата выполнения',
        blank=True,
        null=True
    )
    completed_by = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        verbose_name='Выполнил',
        blank=True,
        null=True,
        related_name='completed_reports'
    )
    failure_reason = models.TextField(
        verbose_name='Причина невыполнения',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания статуса',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Статус отчета'
        verbose_name_plural = 'Статусы отчетов'
        unique_together = ['report', 'period_start']
        ordering = ['-period_start',]

    def __str__(self):
        return f'{self.report.name} - {self.get_status_display()} - {self.period_start}'

    @property
    def is_overdue(self):
        if self.status == 'completed':
            return False
        return dt.date.today() > self.due_date


class ReportStatusHistory(models.Model):
    report_status = models.ForeignKey(
        ReportStatus,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Статус отчета'
    )
    old_status = models.CharField(
        verbose_name='Предыдущий статус',
        max_length=20,
        choices=Report.STATUS_CHOICES
    )
    new_status = models.CharField(
        verbose_name='Новый статус',
        max_length=20,
        choices=Report.STATUS_CHOICES
    )
    changed_by = models.ForeignKey(
        ModuleUser,
        on_delete=models.SET_NULL,
        verbose_name='Изменил',
        blank=True,
        null=True
    )
    changed_at = models.DateTimeField(
        verbose_name='Время изменения',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'История статуса'
        verbose_name_plural = 'История статусов'
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.report_status.report.name} - {self.old_status} → {self.new_status}'
