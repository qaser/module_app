from django.db import models

from locations.models import Department

PARAMETER_TYPE = (
    ('Замечание по оборудованию', 'Замечание по оборудованию'),
    ('Замечание 1-го уровня АПК', 'Замечание 1-го уровня АПК'),
    ('Замечание 2-го уровня АПК', 'Замечание 2-го уровня АПК'),
    ('Замечание ОЗП', 'Замечание ОЗП'),
    ('Замечание Газнадзор', 'Замечание Газнадзор'),
    ('Замечание Ростехнадзор', 'Замечание Ростехнадзор'),
    ('Рацпредложения', 'Рацпредложения'),
    ('ПАТ', 'ПАТ'),
    ('Техучёба', 'Техучёба'),
    ('Кольцевые сварные соединения РЭП', 'Кольцевые сварные соединения РЭП'),
)


class ReportParameter(models.Model):
    title = models.CharField(
        verbose_name='Название параметра',
        choices=PARAMETER_TYPE,
        max_length=100,
        blank=False,
        null=False,
    )
    period = models.PositiveIntegerField(
        'Периодичность отчёта, дн.',
        blank=False,
        null=False,
    )
    class Meta:
        ordering = ('period',)
        verbose_name = 'Параметр доклада'
        verbose_name_plural = 'Параметры доклада'

    def __str__(self) -> str:
        return self.title


class ReportValue(models.Model):
    parameter = models.ForeignKey(
        ReportParameter,
        related_name='parameter',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Служба',
        related_name='departments',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    author = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        verbose_name='Ответственное лицо',
        related_name='faults',
        blank=False,
        null=False,
    )
    description = models.CharField(
        'Дополнительная информация',
        max_length=1000,
        blank=True,
        null=True,
    )
    reg_date = models.DateField(
        'Дата доклада',
        auto_now_add=True,
        blank=False,
        null=False,
    )
    full_num = models.PositiveIntegerField(
        'Общее количество',
        blank=False,
        null=False,
    )
    quarter_num = models.PositiveIntegerField(
        'Количество в текущем квартале',
        blank=True,
        null=True,
    )
    done_num = models.PositiveIntegerField(
        'Выполнено',
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ('reg_date',)
        verbose_name = 'Доклад'
        verbose_name_plural = 'Доклады'

    def __str__(self) -> str:
        return f'{self.department} | {self.reg_date}'
