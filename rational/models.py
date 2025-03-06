from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists, OuterRef, Subquery
from django.db.models.signals import m2m_changed, post_save, post_init
from django.dispatch import receiver
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

from equipments.models import Equipment
from module_app.notifications import NotificationService
from module_app.utils import compress_image
from users.models import ModuleUser, NotificationAppRoute


CATEGORY = (
    ('Использование списанного оборудования', 'Использование списанного оборудования'),
    ('Повышение безопасности труда', 'Повышение безопасности труда'),
    ('Повышение надежности работы оборудования', 'Повышение надежности работы оборудования'),
    ('Снижение трудозатрат', 'Снижение трудозатрат'),
    ('Улучшение условий труда', 'Улучшение условий труда'),
    ('Улучшение условий труда', 'Улучшение условий труда'),
    ('Экономия МТР', 'Экономия МТР'),
    ('Экономия газа', 'Экономия газа'),
    ('Экономия теплоэнергии', 'Экономия теплоэнергии'),
    ('Экономия электроэнергии', 'Экономия электроэнергии'),
    ('Экология', 'Экология'),
)
YEAR_CHOICES = [(year, year) for year in range(2025, 2031)]  # Выбор года
QUARTER_CHOICES = [
    (1, 'Первый квартал'),
    (2, 'Второй квартал'),
    (3, 'Третий квартал'),
    (4, 'Четвертый квартал'),
]


class Proposal(models.Model):
    reg_num = models.CharField(
        'Регистрационный номер',
        max_length=50,
        null=True,
        blank=True,
    )
    reg_date = models.DateTimeField('Дата регистрации', auto_now_add=True,)
    authors = models.ManyToManyField(
        ModuleUser,
        related_name='proposals',
        verbose_name='Автор(ы) предложения',
        blank=False,
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Подразделение'
    )
    category = models.CharField(
        verbose_name='Классификатор',
        choices=CATEGORY,
        max_length=50,
        blank=False,
        null=False
    )
    title = models.CharField(
        'Наименование предложения',
        max_length=200,
        blank=False,
        null=False
    )
    description = models.CharField(
        'Описание предложения',
        max_length=2000,
        blank=False,
        null=False
    )
    is_economy = models.BooleanField(
        'С экономическим эффектом',
        default=False
    )
    economy_size = models.FloatField(
        'Экономический эффект, руб',
        default=0,
        null=True,
        blank=True,
    )
    note = models.CharField(
        'Примечание',
        default='',
        max_length=500,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('reg_date',)
        verbose_name = 'Рационализаторское предложение'
        verbose_name_plural = 'Рационализаторские предложения'

    def __str__(self):
        return f'№{self.reg_num}, {self.title}'

    def get_ks(self):
        """
        Возвращает корневой элемент второго уровня для текущего оборудования.
        """
        if self.equipment:
            # Получаем корень ветки
            root = self.equipment.get_root()
            # Получаем всех потомков корня
            descendants = root.get_descendants(include_self=True)
            # Фильтруем элементы второго уровня
            second_level = descendants.filter(level=1)
            if second_level.exists():
                return second_level.first()
        return None


@receiver(m2m_changed, sender=Proposal.authors.through)
def set_equipment_from_author(sender, instance, action, **kwargs):
    if action == "post_add" and not instance.equipment:
        if instance.authors.exists():
            first_author = instance.authors.first()
            instance.equipment = first_author.equipment
            instance.save()

@receiver(m2m_changed, sender=Proposal.authors.through)
def create_status_with_owner(sender, instance, action, **kwargs):
    if action == "post_add" and not instance.statuses.exists():
        Status.objects.create(
            proposal=instance,
            status=Status.StatusChoices.REG,
            owner=instance.authors.first(),
            note=instance.note,
        )

@receiver(post_save, sender=Proposal)
def set_proposal_reg_num(sender, instance, created, **kwargs):
    """Автоматически устанавливает reg_num после создания Proposal."""
    if created and not instance.reg_num:  # Только для новых объектов без номера
        year = instance.reg_date.year  # Берем год из даты регистрации
        count = Proposal.objects.count()  # Количество записей в БД
        economy_suffix = '-Э' if instance.is_economy else ''
        instance.reg_num = f'2430-{count}-{year}{economy_suffix}'
        instance.save(update_fields=['reg_num'])  # Обновляем только reg_num


class ProposalImage(models.Model):
    image = models.ImageField(
        'Фото РП',
        upload_to='rational/images',
        blank=True,
        null=True,
    )
    name = models.CharField(
        'Наименование фотографии',
        max_length=50,
        blank=True,
        null=True,
    )
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='images'
    )

    class Meta:
        verbose_name = 'Фотоматериалы по РП'
        verbose_name_plural = 'Фотоматериалы по РП'

    def save(self, *args, **kwargs):  # сжатие фото перед сохранением
        super(ProposalImage, self).save(*args, **kwargs)
        if self.image:
            compress_image(self.image)


class ProposalDocument(models.Model):
    doc = models.FileField(upload_to='proposal/docs')
    name = models.CharField(
        'Наименование документа',
        max_length=50,
        blank=False,
        null=False,
    )
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='proposal_doc'
    )

    class Meta:
        verbose_name = 'Документация РП'
        verbose_name_plural = 'Документация РП'


class Status(models.Model):
    class StatusChoices(models.TextChoices):
        REG = 'reg', 'Зарегистрировано'
        RECHECK = 'recheck', 'Повторная заявка'
        REWORK = 'rework', 'Доработать'
        ACCEPT = 'accept', 'Принято'
        REJECT = 'reject', 'Отклонено'
        APPLY = 'apply', 'Используется'

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='statuses',
        verbose_name='РП',
    )
    status = models.CharField(max_length=20, choices=StatusChoices.choices)
    date_changed = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        ModuleUser,
        related_name='owners',
        on_delete=models.SET_NULL,
        verbose_name='Автор',
        blank=True,
        null=True,
    )
    note = models.CharField(
        'Примечание',
        default='',
        max_length=500,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Статус РП'
        verbose_name_plural = 'Статусы РП'

    def clean(self):
        # Статусы, которые могут быть добавлены только один раз
        single_instance_statuses = [
            self.StatusChoices.REG,
            self.StatusChoices.ACCEPT,
            self.StatusChoices.REJECT,
            self.StatusChoices.APPLY,
        ]
        if self.status in single_instance_statuses:
            # Проверяем, есть ли уже такой статус у предложения
            if Status.objects.filter(
                proposal=self.proposal,
                status=self.status
            ).exists():
                raise ValidationError(
                    f'Статус "{self.get_status_display()}" уже существует для этого РП.'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


@receiver(post_save, sender=Status)
def send_notification(sender, instance, created, **kwargs):
    recipients = []
    # 1. Отправляем ответственному за приложение, если статус reg или recheck
    if instance.status in [instance.StatusChoices.REG, instance.StatusChoices.RECHECK]:
        app_route = NotificationAppRoute.objects.filter(app_name='rational').first()
        if app_route and app_route.user:
            recipients.append(app_route.user.email)
    # 2. Отправляем авторам, если статус rework, accept, reject, apply
    if instance.status in [instance.StatusChoices.REWORK, instance.StatusChoices.ACCEPT, instance.StatusChoices.REJECT, instance.StatusChoices.APPLY]:
        recipients += list(instance.proposal.authors.values_list('email', flat=True))
    # Отправка email
    if recipients:
        subject = f'Изменение статуса РП №{instance.proposal.reg_num}'
        message = (
            f'Статус рационализаторского предложения №{instance.proposal.reg_num} изменен.\n'
            f'Новый статус: {instance.get_status_display()}\n'
            f"Дата изменения: {instance.date_changed.strftime('%d.%m.%Y, %H:%M')}\n"
            f"Примечание: {instance.note or 'Без примечаний'}"
        )
        print(instance.status, recipients)
        # self.send_email(self.owner.email, subject, message)


class Plan(MPTTModel):
    year = models.IntegerField(
        'Год',
        choices=YEAR_CHOICES,
        blank=False,
        null=False,
    )
    quarter = models.IntegerField(
        'Квартал',
        choices=QUARTER_CHOICES,
        blank=True,
        null=True,  # Если план на год, а не на квартал
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        verbose_name='Подразделение',
        blank=True,
        null=True,
    )
    target = models.IntegerField(
        'Плановое количество предложений',
        blank=False,
        null=False,
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский план'
    )

    class Meta:
        verbose_name = 'План'
        verbose_name_plural = 'Планы'
        unique_together = ('year', 'quarter', 'equipment', 'parent')

    class MPTTMeta:
        order_insertion_by = ['year', 'quarter']

    def __str__(self):
        if self.quarter:
            return f'План на {self.year} год, {self.equipment.name}'
        return f'План на {self.year} год, {self.equipment.name} '

    @property
    def completed(self):
        if self.is_leaf_node():
            # Определяем диапазон дат для квартала
            start_date = datetime(self.year, 3 * (self.quarter - 1) + 1, 1)  # Начало квартала
            if self.quarter == 4:
                end_date = datetime(self.year + 1, 1, 1) - timedelta(days=1)  # Конец квартала (31 декабря)
            else:
                end_date = datetime(self.year, 3 * self.quarter + 1, 1) - timedelta(days=1)  # Конец квартала
            # Подзапрос для проверки наличия статуса ACCEPT
            has_accept_status = Status.objects.filter(
                proposal=OuterRef('id'),
                status=Status.StatusChoices.ACCEPT
            )
            # Фильтруем предложения, которые получили статус REG в указанный период
            # и имеют хотя бы один статус ACCEPT
            accepted_proposals = Proposal.objects.filter(
                statuses__status=Status.StatusChoices.REG,
                statuses__date_changed__gte=start_date,
                statuses__date_changed__lte=end_date,
                equipment=self.equipment
            ).annotate(
                has_accept=Exists(has_accept_status)
            ).filter(
                has_accept=True
            ).distinct().count()
            return accepted_proposals
        else:
            # Для нелистовых узлов (годовых планов) суммируем значения из дочерних узлов
            return sum(child.completed for child in self.get_children())
