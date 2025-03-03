from django.db import models
from django.db.models import OuterRef, Subquery
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

from equipments.models import Equipment
from module_app.utils import compress_image
from users.models import ModuleUser

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
        REWORK = 'rework', 'На доработке'  # зациклить с recheck
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
        verbose_name='Автор(ы)',
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

    from django.db.models import OuterRef, Subquery

    @property
    def completed(self):
        """
        Вычисляемое поле: количество заявок, принятых в рамках плана.
        """
        if self.is_leaf_node():
            # Определяем диапазон дат для квартала
            start_date = f'{self.year}-{3 * (self.quarter - 1) + 1:02d}-01'  # Начало квартала
            end_date = f'{self.year}-{3 * self.quarter:02d}-31'  # Конец квартала

            # Подзапрос для получения последнего статуса каждого предложения
            latest_statuses = Status.objects.filter(
                proposal=OuterRef('id')
            ).order_by('-date_changed').values('status')[:1]

            # Фильтруем предложения, у которых статус REG был в указанном диапазоне,
            # и последний статус — ACCEPT
            accepted_proposals = Proposal.objects.annotate(
                latest_status=Subquery(latest_statuses)
            ).filter(
                statuses__status=Status.StatusChoices.REG,
                statuses__date_changed__gte=start_date,
                statuses__date_changed__lte=end_date,
                equipment=self.equipment,
                latest_status=Status.StatusChoices.ACCEPT
            ).distinct().count()

            return accepted_proposals
        else:
            # Для нелистовых узлов (годовых планов) суммируем значения из дочерних узлов
            return sum(child.completed for child in self.get_children())
