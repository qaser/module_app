from django.db import models

from equipments.models import Equipment
from leaks.utils import compress_image
from tpa.models import Valve
from users.models import ModuleUser

PLACE = (('КЦ', 'КЦ'), ('ЛЧ', 'ЛЧ'),)
DOCTYPE = (
    ('Протокол', 'Протокол'),
    ('Донесение об утечке газа', 'Донесение об утечке газа'),
)
FILETYPE = (('video', 'video'), ('image', 'image'))


class Leak(models.Model):
    # direction = models.ForeignKey(
    #     Direction,
    #     verbose_name='Структурное подразделение',
    #     related_name='directions',
    #     on_delete=models.CASCADE,
    # )
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
        related_name='locations',
        on_delete=models.CASCADE
    )
    is_valve = models.BooleanField(
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
    detector = models.CharField(
        verbose_name='Кем выявлена утечка',
        max_length=50,
        blank=False,
        null=False,
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
    is_done = models.BooleanField(
        verbose_name='Устранено',
        default=False,
    )
    note = models.CharField(
        verbose_name='План работ',
        max_length=500,
        blank=False,
        null=False,
    )
    is_draft = models.BooleanField(
        verbose_name='Черновик',
        default=True,
    )


    class Meta:
        ordering = ('detection_date',)
        verbose_name = 'Утечка'
        verbose_name_plural = 'Утечки'

    def __str__(self):
        return f'{self.detection_date}, {self.location}, {self.description}'


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
