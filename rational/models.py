import os
import tempfile
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count, Exists, OuterRef, Q, Sum
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

from equipments.models import Department
from module_app.utils import compress_image
from notifications.models import Notification
from users.models import ModuleUser, UserAppRoute

from .utils import create_doc

CATEGORY = (
    ('Использование списанного оборудования', 'Использование списанного оборудования'),
    ('Повышение безопасности труда', 'Повышение безопасности труда'),
    ('Повышение надежности работы оборудования', 'Повышение надежности работы оборудования'),
    ('Снижение трудозатрат', 'Снижение трудозатрат'),
    ('Улучшение условий труда', 'Улучшение условий труда'),
    ('Экономия МТР', 'Экономия МТР'),
    ('Экономия газа', 'Экономия газа'),
    ('Экономия теплоэнергии', 'Экономия теплоэнергии'),
    ('Экономия электроэнергии', 'Экономия электроэнергии'),
    ('Экология', 'Экология'),
)
current_year = datetime.now().year
YEAR_CHOICES = [(year, year) for year in range(current_year, current_year + 6)]
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
    reg_date = models.DateTimeField(
        'Дата регистрации',
        default=timezone.now,
    )
    authors = models.ManyToManyField(
        ModuleUser,
        related_name='proposals',
        verbose_name='Автор(ы) предложения',
        blank=False,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
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
        max_length=500,
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
    # Флаг для отслеживания готовности к созданию файла
    is_ready = models.BooleanField(default=False)

    class Meta:
        ordering = ('reg_date',)
        verbose_name = 'Рационализаторское предложение'
        verbose_name_plural = 'Рационализаторские предложения'
        indexes = [
            models.Index(fields=['reg_num']),  # Уникальный идентификатор
            models.Index(fields=['reg_date']),
            models.Index(fields=['department']),  # Фильтрация по подразделению
            models.Index(fields=['category']),  # Фильтрация по категории
            models.Index(fields=['is_economy']),  # Фильтрация по флагу экономии
            models.Index(fields=['reg_date', 'department']),  # Комбинированный
        ]

    def __str__(self):
        return f'№{self.reg_num}, {self.title}'

    def get_ks(self):
        if self.department:
            # Получаем корень ветки
            root = self.department.get_root()
            # Получаем всех потомков корня
            descendants = root.get_descendants(include_self=True)
            # Фильтруем элементы второго уровня
            second_level = descendants.filter(level=1)
            if second_level.exists():
                return second_level.first()
        return None


@receiver(m2m_changed, sender=Proposal.authors.through)
def set_department_from_author(sender, instance, action, **kwargs):
    if action == "post_add" and not instance.department:
        if instance.authors.exists():
            first_author = instance.authors.first()
            instance.department = first_author.department
            instance.save()


@receiver(m2m_changed, sender=Proposal.authors.through)
def create_status_with_owner(sender, instance, action, **kwargs):
    if action == "post_add" and not instance.statuses.exists():
        ProposalStatus.objects.create(
            proposal=instance,
            status=ProposalStatus.StatusChoices.REG,
            owner=instance.authors.first(),
            note=instance.note,
        )


@receiver(post_save, sender=Proposal)
def set_proposal_reg_num(sender, instance, created, **kwargs):
    """Автоматически устанавливает reg_num после создания Proposal."""
    if created and not instance.reg_num:
        year = instance.reg_date.year
        count = Proposal.objects.filter(reg_date__year=year).count()
        economy_suffix = '-Э' if instance.is_economy else ''
        instance.reg_num = f'2430-{count + 1}-{year}{economy_suffix}'
        instance.save(update_fields=['reg_num'])


@receiver(post_save, sender=Proposal)
def handle_post_save(sender, instance, created, **kwargs):
    """Обработчик сигнала post_save."""
    if created:
        # Устанавливаем флаг is_ready, если авторы уже добавлены
        if instance.authors.exists():
            instance.is_ready = True
            instance.save()
            create_proposal_doc(instance)
        else:
            # Ждем сигнала m2m_changed для добавления авторов
            pass


@receiver(m2m_changed, sender=Proposal.authors.through)
def handle_m2m_changed(sender, instance, action, **kwargs):
    """Обработчик сигнала m2m_changed."""
    if action == 'post_add':  # Срабатывает после добавления авторов
        if not instance.is_ready:
            instance.is_ready = True
            instance.save()
            create_proposal_doc(instance)


def create_proposal_doc(instance):
    """Создает заявление в формате docx для Proposal."""
    if instance.is_ready:
        department = instance.department
        root_department = department
        while root_department.parent:
            root_department = root_department.parent
        app_user = UserAppRoute.objects.filter(
            department=root_department,
            app_name='rational'
        ).first()
        proposal_doc_dict = {
            'department': root_department.name,
            'appuser': app_user.user.fio,
            'title': instance.title,
            'equipment': department.name,
            'description': instance.description,
            'author0': '',
            'direction0': '',
            'jobposition0': '',
            'author1': '',
            'direction1': '',
            'jobposition1': '',
            'author2': '',
            'direction2': '',
            'jobposition2': '',
            'author3': '',
            'direction3': '',
            'jobposition3': '',
            'role0': '',
            'role1': '',
            'role2': '',
            'role3': '',
        }
        for id, author in enumerate(instance.authors.all()):
            proposal_doc_dict[f'author{id}'] = author.fio
            proposal_doc_dict[f'direction{id}'] = author.department.name
            proposal_doc_dict[f'jobposition{id}'] = author.job_position
            proposal_doc_dict[f'role{id}'] = 'Автор идеи'
        doc = create_doc(proposal_doc_dict)
        # Сохраняем документ во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            doc.save(tmp_file)
            tmp_file_path = tmp_file.name
        # Сохраняем файл в объекте ProposalDocument
        reg_date = instance.reg_date.strftime('%d.%m.%Y')
        file_name = f'Заявление РП №{instance.reg_num}.docx'
        with open(tmp_file_path, 'rb') as file:
            proposal_doc = ProposalDocument(
                name=file_name,
                proposal=instance
            )
            proposal_doc.doc.save(file_name, File(file))
            proposal_doc.save()
        # Удаляем временный файл
        os.remove(tmp_file_path)


class ProposalDocument(models.Model):
    doc = models.FileField(upload_to='rational/docs')
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
        indexes = [
            models.Index(fields=['proposal']),  # Основной фильтр
        ]


class ProposalStatus(models.Model):
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
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices
    )
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
        indexes = [
            models.Index(fields=['proposal']),
            models.Index(fields=['status']),  # Фильтрация по статусу
            models.Index(fields=['date_changed']),  # Сортировка по дате
            models.Index(fields=['proposal', 'status']),  # Комбинированный
        ]

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
            if ProposalStatus.objects.filter(
                proposal=self.proposal,
                status=self.status
            ).exists():
                raise ValidationError(
                    f'Статус "{self.get_status_display()}" уже существует для этого РП.'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


@receiver(post_save, sender=ProposalStatus)
def send_notification(sender, instance, created, **kwargs):
    if not created:
        return

    notification_data = {
        'app_name': Notification.AppChoices.RATIONAL,
        'object_id': instance.proposal.id,
        'title': f'Изменение статуса РП №{instance.proposal.reg_num}',
        'message': f'Статус изменен на: {instance.get_status_display()}',
        'status': instance.status
    }
    # 1. Отправляем ответственному за приложение, если статус reg или recheck
    if instance.status in [instance.StatusChoices.REG, instance.StatusChoices.RECHECK]:
        root_department = instance.proposal.department.get_root()
        # Ищем UserAppRoute по app_name и корневому department
        app_route = UserAppRoute.objects.filter(app_name='rational', department=root_department).first()
        if app_route and app_route.user:
            Notification.objects.create(user=app_route.user, **notification_data)
    # 2. Отправляем авторам, если статус rework, accept, reject, apply
    if instance.status in [
        instance.StatusChoices.REWORK,
        instance.StatusChoices.ACCEPT,
        instance.StatusChoices.REJECT,
        instance.StatusChoices.APPLY
    ]:
        for author in instance.proposal.authors.all():
            Notification.objects.create(user=author, **notification_data)


class AnnualPlan(models.Model):
    department = TreeForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='plans',
        verbose_name='Подразделение'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год планирования',
        choices=[(y, y) for y in range(datetime.now().year, datetime.now().year + 6)]
    )
    total_proposals = models.PositiveIntegerField(
        verbose_name='Запланированное количество РП',
        default=0
    )
    total_economy = models.FloatField(
        verbose_name='Ожидаемый экономический эффект, руб.',
        default=0.0,
    )

    class Meta:
        # unique_together = ('department', 'year')
        verbose_name = 'Годовой план'
        verbose_name_plural = 'Годовые планы'
        indexes = [
            models.Index(fields=['department']),  # Фильтрация по подразделению
            models.Index(fields=['year']),  # Фильтрация по году
            models.Index(fields=['department', 'year']),  # Уникальный вместе
        ]

    def __str__(self):
        return f'{self.department.name} - {self.year}'

    @property
    def completed_proposals(self):
        """
        Возвращает количество предложений, зарегистрированных и принятых в данном году
        для данного оборудования и его дочерних элементов.
        """
        return sum(quarter.completed_proposals for quarter in self.quarterly_plans.all())

    @property
    def sum_economy(self):
        """
        Возвращает сумму экономии всех предложений, зарегистрированных и принятых
        в данном году для данного оборудования и его дочерних элементов
        """
        return sum(quarter.sum_economy for quarter in self.quarterly_plans.all())


class QuarterlyPlan(models.Model):
    """
    Квартальный план, привязанный к годовому.
    """
    annual_plan = models.ForeignKey(
        AnnualPlan,
        on_delete=models.CASCADE,
        related_name='quarterly_plans',
        verbose_name='Годовой план'
    )
    quarter = models.PositiveSmallIntegerField(
        verbose_name='Квартал',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')]
    )
    planned_proposals = models.PositiveIntegerField(
        verbose_name='Запланированное количество РП',
        default=0
    )
    planned_economy = models.FloatField(
        verbose_name='Ожидаемый экономический эффект, руб.',
        default=0.0
    )

    class Meta:
        # unique_together = ('annual_plan', 'quarter')
        verbose_name = 'Квартальный план'
        verbose_name_plural = 'Квартальные планы'
        indexes = [
            models.Index(fields=['annual_plan']),  # Основной фильтр
            models.Index(fields=['quarter']),  # Фильтрация по кварталу
            models.Index(fields=['annual_plan', 'quarter']),  # Уникальный вместе
        ]

    def get_quarter_date_range(self):
        """Возвращает диапазон дат для заданного квартала."""
        year = self.annual_plan.year
        quarter = self.quarter
        if quarter == 1:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 3, 31)
        elif quarter == 2:
            start_date = datetime(year, 4, 1)
            end_date = datetime(year, 6, 30)
        elif quarter == 3:
            start_date = datetime(year, 7, 1)
            end_date = datetime(year, 9, 30)
        elif quarter == 4:
            start_date = datetime(year, 10, 1)
            end_date = datetime(year, 12, 31)
        return start_date, end_date

    @property
    def completed_proposals(self):
        """
        Возвращает количество предложений, зарегистрированных и принятых в данном
        квартале для данного оборудования и его дочерних элементов
        """
        start_date, end_date = self.get_quarter_date_range()
        # Получаем все дочерние элементы текущего оборудования
        department_ids = self.annual_plan.department.get_descendants(include_self=True).values_list('id', flat=True)
        # Фильтруем предложения по department и статусам
        proposals = Proposal.objects.filter(
            reg_date__range=(start_date, end_date),
            department__id__in=department_ids,  # Только для текущего оборудования и его дочерних элементов
            statuses__status=ProposalStatus.StatusChoices.REG,
        ).filter(
            statuses__status=ProposalStatus.StatusChoices.ACCEPT
        ).distinct()
        return proposals.count()

    @property
    def sum_economy(self):
        """
        Возвращает сумму экономии всех предложений, зарегистрированных и принятых в
        данном квартале для данного оборудования и его дочерних элементов
        """
        start_date, end_date = self.get_quarter_date_range()
        department_ids = self.annual_plan.department.get_descendants(include_self=True).values_list('id', flat=True)
        # Фильтруем предложения по department и статусам
        proposals = Proposal.objects.filter(
            reg_date__range=(start_date, end_date),
            department__id__in=department_ids,  # Только для текущего оборудования и его дочерних элементов
            statuses__status=ProposalStatus.StatusChoices.REG,
        ).filter(
            statuses__status=ProposalStatus.StatusChoices.ACCEPT
        ).distinct()
        return proposals.aggregate(total_economy=Sum('economy_size'))['total_economy'] or 0


@receiver(post_save, sender=AnnualPlan)
def create_quarterly_plans(sender, instance, created, **kwargs):
    """
    Автоматически создаем квартальные планы после создания годового плана
    """
    if created:
        for quarter in range(1, 5):
            QuarterlyPlan.objects.create(
                annual_plan=instance,
                quarter=quarter,
                planned_proposals=instance.total_proposals // 4,
                planned_economy=instance.total_economy / 4
            )


@receiver(post_save, sender=AnnualPlan)
def create_subdivision_plans(sender, instance, created, **kwargs):
    """
    Автоматически создаем годовые планы для дочерних подразделений
    """
    if created:
        children = instance.department.get_children()
        for child in children:
            AnnualPlan.objects.create(
                department=child,
                year=instance.year,
                total_proposals=instance.total_proposals // len(children) if children else 0,
                total_economy=instance.total_economy / len(children) if children else 0
            )
