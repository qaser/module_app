from django.core.exceptions import ValidationError
from django.db import models

from equipments.models import Equipment
from leaks.utils import compress_image
from tpa.models import Valve
from users.models import ModuleUser

PLACE = (('КЦ', 'КЦ'), ('ЛЧ', 'ЛЧ'),)
FILETYPE = (('video', 'video'), ('image', 'image'))
DETECTOR_TYPE = (
    ('Эксплуатационный персонал', 'Эксплуатационный персонал'),
    ('Ремонтный персонал', 'Ремонтный персонал'),
    ('Административная проверка', 'Административная проверка'),
    ('Контролирующая организация', 'Контролирующая организация'),
)
DOCTYPE = (
    ('Протокол', 'Протокол'),
    ('Донесение об утечке газа', 'Донесение об утечке газа'),
)


class Leak(models.Model):
    place = models.CharField(
        'Местоположение утечки',
        choices=PLACE,
        max_length=50,
        blank=False,
        null=False
    )
    equipment = models.ForeignKey(
        Equipment,
        verbose_name='Наименование объекта',
        related_name='equipments',
        on_delete=models.CASCADE
    )
    on_valve = models.BooleanField(
        verbose_name='Утечка по ТПА',
        default=False,
    )
    valve = models.ForeignKey(
        Valve,
        verbose_name='Наименование ТПА',
        related_name='valves',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    specified_location = models.CharField(
        'Уточненное местоположение',
        max_length=100,
        blank=True,
        null=True,
    )
    description = models.CharField(
        verbose_name='Описание утечки',
        max_length=500,
        blank=False,
        null=False,
    )
    type_leak = models.CharField(
        verbose_name='Тип утечки',
        max_length=100,
        blank=False,
        null=False,
    )
    volume = models.FloatField(
        'Объем потерь газа, м3/сут',
        blank=True,
        null=True,
    )
    volume_dinamic = models.FloatField(
        'Объем потерь газа нарастающий, тыс. м3',
        blank=True,
        null=True,
    )
    gas_losses = models.FloatField(
        'Потери газа в тыс. руб.',
        blank=True,
        null=True,
    )
    reason = models.CharField(
        verbose_name='Причина возникновения',
        max_length=100,
        blank=False,
        null=False,
    )
    detection_date = models.DateField(
        'Дата выявления',
        blank=False,
        null=False,
    )
    planned_date = models.DateField(
        'Плановый срок устранения',
        blank=False,
        null=False,
    )
    fact_date = models.DateField(
        'Фактический срок устранения',
        blank=True,
        null=True,
    )
    method = models.CharField(
        verbose_name='Способ устранения',
        max_length=100,
        blank=False,
        null=False,
    )
    detector_type = models.CharField(
        verbose_name='Кем выявлена утечка',
        choices=DETECTOR_TYPE,
        max_length=50,
        blank=False,
        null=False,
    )
    detector = models.ForeignKey(
        ModuleUser,
        on_delete=models.SET_NULL,
        verbose_name='Кто обнаружил',
        related_name='detectors',
        blank=True,
        null=True,
    )
    executor = models.ForeignKey(
        ModuleUser,
        on_delete=models.CASCADE,
        verbose_name='Ответственный за устранение',
        related_name='users'
    )
    plan_work = models.CharField(
        verbose_name='План работ',
        max_length=500,
        blank=False,
        null=False,
    )
    doc_name = models.CharField(
        verbose_name='Метод определения',
        max_length=100,
        blank=False,
        null=False,
    )
    protocol = models.CharField(
        verbose_name='Протокол',
        max_length=100,
        blank=False,
        null=False,
    )
    # is_done = models.BooleanField(
    #     verbose_name='Устранено',
    #     default=False,
    # )
    note = models.CharField(
        verbose_name='Примечание',
        max_length=500,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ('detection_date',)
        verbose_name = 'Утечка'
        verbose_name_plural = 'Утечки'

    def __str__(self):
        return f'{self.detection_date}, {self.equipment}, {self.description}'


class LeakDocument(models.Model):
    doc = models.FileField(upload_to='leaks/docs')
    name = models.CharField(
        'Наименование документа',
        choices=DOCTYPE,
        max_length=50,
        blank=False,
        null=False,
    )
    leak = models.ForeignKey(
        Leak,
        on_delete=models.CASCADE,
        related_name='leak_doc'
    )

    class Meta:
        verbose_name = 'Документация по утечке газа'
        verbose_name_plural = 'Документация по утечке газа'


class LeakImage(models.Model):
    image = models.ImageField(
        'Фото утечки газа',
        upload_to='leaks/images',
        default='leaks/image_not_upload.png',
        blank=True,
        null=True,
    )
    name = models.CharField(
        'Наименование фотографии',
        max_length=50,
        blank=True,
        null=True,
    )
    leak = models.ForeignKey(
        Leak,
        on_delete=models.CASCADE,
        related_name='images'
    )

    class Meta:
        verbose_name = 'Фотоматериалы по утечке'
        verbose_name_plural = 'Фотоматериалы по утечке'

    def save(self, *args, **kwargs):  # сжатие фото перед сохранением
        super(LeakImage, self).save(*args, **kwargs)
        if self.image:
            compress_image(self.image)


class LeakStatus(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        REG = 'reg', 'Зарегистрирована'
        FIXED = 'fixed', 'Устранена'

    leak = models.ForeignKey(
        Leak,
        on_delete=models.CASCADE,
        related_name='statuses',
        verbose_name='Утечка',
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices
    )
    date_changed = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        ModuleUser,
        related_name='status_owner',
        on_delete=models.SET_NULL,
        verbose_name='Пользователь',
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
        verbose_name = 'Статус утечки газа'
        verbose_name_plural = 'Статусы утечки газа'
        constraints = [
            models.UniqueConstraint(
                fields=['leak', 'status'],
                name='unique_status_per_leak',
            ),
        ]

    def clean(self):
        if self.status in ['reg', 'fixed', 'draft']:
            if LeakStatus.objects.filter(leak=self.leak, status=self.status).exists():
                raise ValidationError(
                    f'Статус "{self.get_status_display()}" уже существует для этой утечки.'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
