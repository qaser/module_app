from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone

from equipments.models import Equipment
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
        blank=False,
        null=False,
    )
    reg_date = models.DateField(
        'Дата регистрации',
        default=timezone.now,
        blank=False,
        null=False,
    )
    check_date = models.DateField(
        'Дата проверки',
        blank=True,
        null=True,
    )
    accept_date = models.DateField(
        'Дата признания рационализаторским',
        blank=True,
        null=True,
    )
    reject_date = models.DateField(
        'Дата отклонения',
        blank=True,
        null=True,
    )
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
        verbose_name='Структура предприятия'
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
        null=True,
        blank=True,
    )
    is_apply = models.BooleanField(
        'Принято к использованию',
        default=False
    )
    is_reject = models.BooleanField(
        'Отклонено',
        default=False
    )
    apply_date = models.DateField(
        'Дата начала использования',
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
        ordering = ('reg_date',)
        verbose_name = 'Рационализаторское предложение'
        verbose_name_plural = 'Рационализаторские предложения'

    def __str__(self):
        return f'№{self.reg_num}, {self.equipment}'


@receiver(m2m_changed, sender=Proposal.authors.through)
def set_equipment_from_author(sender, instance, action, **kwargs):
    if action == "post_add" and not instance.equipment:
        if instance.authors.exists():
            first_author = instance.authors.first()
            instance.equipment = first_author.equipment
            instance.save()


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
        # Вычисляемое поле: количество заявок, зарегистрированных в рамках плана.
        if self.is_leaf_node():
            # Для квартальных планов
            start_date = f'{self.year}-{3 * (self.quarter - 1) + 1:02d}-01'  # Начало квартала
            end_date = f'{self.year}-{3 * self.quarter:02d}-31'  # Конец квартала

            return Proposal.objects.filter(
                accept_date__gte=start_date,
                accept_date__lte=end_date,
                equipment=self.equipment,
            ).count()
        else:
            # Для нелистовых узлов (годовых планов)
            return sum(child.completed for child in self.get_children())
