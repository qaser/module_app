from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from equipments.models import Department


class Pipeline(models.Model):
    name = models.CharField('Название газопровода', max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Газопровод'
        verbose_name_plural = 'Газопроводы'

    def __str__(self):
        return self.name


class Pipe(models.Model):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='%(app_label)s_%(class)s',
    )
    diameter = models.PositiveIntegerField(
        'Диаметр, мм',
        blank=True,
        null=True
    )
    start_point = models.FloatField(
        verbose_name='Начало участка, км',
        blank=False,
        null=False
    )
    end_point = models.FloatField(
        verbose_name='Конец участка, км',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Участок газопровода'
        verbose_name_plural = 'Участки газопроводов'
        ordering = ['start_point']


class ValveNode(models.Model):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='%(app_label)s_%(class)s',
    )
    valve_point = models.FloatField(
        verbose_name='Место расположения, км',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Крановый узел'
        verbose_name_plural = 'Крановые узлы'
        ordering = ['valve_point']


class ConnectionNode(models.Model):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='%(app_label)s_%(class)s',
    )
    connect_point = models.FloatField(
        verbose_name='Место подключения, км',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Узел подключения'
        verbose_name_plural = 'Узлы подключения'
        ordering = ['connect_point']


class BridgeNode(models.Model):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='%(app_label)s_%(class)s',
    )
    bridge_point = models.FloatField(
        verbose_name='Место перемыки, км',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Перемычка'
        verbose_name_plural = 'Перемычки'
        ordering = ['bridge_point']
