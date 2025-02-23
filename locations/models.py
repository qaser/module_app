from django.db import models

STRUCTURE_TYPE = (
    ('АУП', 'АУП'),
    ('Филиал', 'Филиал'),
)


class Structure(models.Model):
    structure_type = models.CharField(
        verbose_name='Структура Общества',
        choices=STRUCTURE_TYPE,
        max_length=50,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Структура'
        verbose_name_plural = 'Структуры'

    def __str__(self) -> str:
        return self.structure_type


class Direction(models.Model):
    name = models.CharField('Наименование филиала', max_length=50)
    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Филиал'
        verbose_name_plural = 'Филиалы'

    def __str__(self) -> str:
        return self.name


class Station(models.Model):
    name = models.CharField('Наименование КС', max_length=50)
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'КС'
        verbose_name_plural = 'КС'

    def __str__(self) -> str:
        return self.name


# структурное подразделение (ГКС разделять по цехам, остальное по службам )
class Department(models.Model):
    name = models.CharField(
        'Название подразделения',
        max_length=50,
    )
    station = models.ForeignKey(
        Station,
        verbose_name = 'КС',
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    part_of = models.CharField(
        'Общее название',
        max_length=25,
        null=False,
        blank=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'station'],
                name='name_of_department_of_station'
            ),
        ]
        ordering = ('name',)
        verbose_name = 'подразделение филиала'
        verbose_name_plural = 'подразделения филиала'

    def __str__(self) -> str:
        return self.name


class TypeOfLocation(models.Model):
    name = models.CharField(
        'Тип оборудования',
        max_length=100,
    )

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    name = models.CharField(
        'Оборудование',
        max_length=100,
    )
    department  = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    type_location = models.ForeignKey(
        TypeOfLocation,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'оборудование'
        verbose_name_plural = 'оборудование'

    def __str__(self) -> str:
        return self.name
