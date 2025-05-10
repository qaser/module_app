from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey

from module_app.utils import get_installed_apps


class Department(MPTTModel):
    name = models.CharField(
        verbose_name='Название',
        max_length=50,
        blank=False,
        null=False
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский объект'
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    def __str__(self):
        return self.name


class Pipeline(models.Model):
    name = models.CharField('Название газопровода', max_length=100)
    code = models.SlugField('Код', unique=True)
    diameter = models.PositiveIntegerField('Диаметр, мм', blank=True, null=True)
    pressure = models.PositiveIntegerField('Давление, кгс/см²', blank=True, null=True)

    class Meta:
        verbose_name = 'Газопровод'
        verbose_name_plural = 'Газопроводы'

    def __str__(self):
        return self.name


class Equipment(MPTTModel):
    name = models.CharField(
        verbose_name='Название',
        max_length=50,
        blank=False,
        null=False
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский объект'
    )
    departments = models.ManyToManyField(
        Department,
        related_name='equipments',
        verbose_name='Подразделения'
    )
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.SET_NULL,
        verbose_name='Газопровод',
        blank=True,
        null=True
    )

    # @property
    # def pipeline(self):
    #     if self.parent:
    #         return self.parent.pipeline
    #     return self._pipeline

    # @pipeline.setter
    # def pipeline(self, value):
    #     if not self.parent:
    #         self._pipeline = value

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'

    def __str__(self) -> str:
        return self.name
