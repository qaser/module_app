from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.db.models.functions import Now

from equipments.models import Department
# from rest_framework.authtoken.models import Token
from module_app.utils import get_installed_apps

APP_CHOICES = [(app, app) for app in get_installed_apps()]
YOUNG_AGE_THRESHOLD = 35  # Порог молодости


class Role(models.TextChoices):
    ADMIN = 'admin'  # всемогущий (просмотр всех equipments)
    MANAGER = 'manager'  # уровень ЛПУМГ (просмотр всех дочерних equipments от самого начала)
    EMPLOYEE = 'employee'  # уровень рабочего места (просмотр всех дочерних equipments своего места работы)


class ActiveUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class ModuleUser(AbstractUser):
    objects = UserManager()
    active_objects = ActiveUserManager()
    patronymic = models.CharField(
        'Отчество',
        max_length=50,
        blank=True,
        null=True,
    )
    job_position = models.TextField('Должность', blank=True, null=True)
    role = models.CharField(
        'Роль пользователя',
        max_length=30,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Место работы'
    )
    service_num = models.CharField(
        'Табельный номер',
        max_length=20,
        blank=True,
        null=True,
    )
    birth_date = models.DateField('Дата рождения', null=True, blank=True)

    class Meta:
        ordering = ('last_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.CheckConstraint(
                check=Q(birth_date__lte=Now()),
                name='birth_date_not_in_future'
            )
        ]

    @property
    def lastname_and_initials(self):
        parts = []
        # Добавляем фамилию, если она есть
        if self.last_name:
            parts.append(self.last_name)
        # Формируем инициалы
        initials = []
        if self.first_name:
            initials.append(f"{self.first_name[0]}." if self.first_name else '')
        if self.patronymic:
            initials.append(f"{self.patronymic[0]}." if self.patronymic else '')
        # Объединяем инициалы без пробелов
        if initials:
            parts.append(''.join(initials))
        return ' '.join(parts) if parts else self.username

    @property
    def fio(self):
        parts = []
        if self.last_name:
            parts.append(self.last_name)
        if self.first_name:
            parts.append(self.first_name)
        if self.patronymic:
            parts.append(self.patronymic)
        return ' '.join(parts) if parts else self.username

    @property
    def is_young_worker(self):
        if not self.birth_date:
            return False
        return self.age < self.YOUNG_AGE_THRESHOLD

    @property
    def age(self):
        return relativedelta(date.today(), self.birth_date).years

    @classmethod
    def get_young_workers(cls):
        threshold_date = date.today() - relativedelta(years=cls.YOUNG_AGE_THRESHOLD)
        return cls.objects.filter(birth_date__gte=threshold_date)

    def __str__(self) -> str:
        if self.last_name and self.first_name:
            return self.lastname_and_initials
        return self.username


class UserAppRoute(models.Model):
    app_name = models.CharField(
        'Приложение',
        max_length=50,
        choices=APP_CHOICES,  # Ограничиваем выбор только установленными приложениями
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name='ЛПУМГ',
        blank=False,
        null=False,
    )
    user = models.ForeignKey(
        ModuleUser,
        related_name='apps',
        on_delete=models.CASCADE,
        verbose_name='Ответственный за приложение',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('app_name',)
        verbose_name = 'Ответственный работник'
        verbose_name_plural = 'Ответственные работники'
