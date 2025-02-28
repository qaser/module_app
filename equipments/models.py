from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey


class TypeOfEquipment(models.Model):
    name = models.CharField(
        'Тип оборудования',
        max_length=100,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тип оборудования'
        verbose_name_plural = 'Тип оборудования'

    def __str__(self) -> str:
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
    type_equipment = models.ForeignKey(
        TypeOfEquipment,
        on_delete=models.SET_NULL,
        verbose_name='Тип оборудования',
        null=True,
        blank=True
    )

    class MPTTMeta:
        order_insertion_by = ['name']  # Сортировка по имени

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'

    def __str__(self) -> str:
        ancestors = self.get_ancestors(ascending=True, include_self=True)[:2]
        return ' | '.join(ancestor.name for ancestor in ancestors)
