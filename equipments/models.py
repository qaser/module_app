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

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'

    def __str__(self) -> str:
        return self.name
