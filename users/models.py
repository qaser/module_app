from django.contrib.auth.models import AbstractUser
from django.db import models
# from rest_framework.authtoken.models import Token
from module_app.utils import get_installed_apps

from equipments.models import Department


APP_CHOICES = [(app, app) for app in get_installed_apps()]


class Role(models.TextChoices):
    ADMIN = 'admin'  # всемогущий (просмотр всех equipments)
    MANAGER = 'manager'  # уровень ЛПУМГ (просмотр всех дочерних equipments от самого начала)
    EMPLOYEE = 'employee'  # уровень рабочего места (просмотр всех дочерних equipments своего места работы)


class ModuleUser(AbstractUser):
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

    class Meta:
        ordering = ('last_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # представление пользователя в виде Фамилия И.О.
    # с учетом отсутствия Отчества
    @property
    def lastname_and_initials(self):
        lastname = self.last_name
        initial_name = self.first_name[0]
        if self.patronymic is not None:
            initial_patronymic = self.patronymic[0]
            lastname_and_initials = (f'{lastname} '
                                     f'{initial_name}.{initial_patronymic}.')
        else:
            lastname_and_initials = f'{lastname} {initial_name}.'
        return lastname_and_initials

    # представление пользователя в виде Фамилия Имя Отчество
    # с учетом отсутствия Отчества
    @property
    def fio(self):
        if self.patronymic is not None:
            fio = f'{self.last_name} {self.first_name} {self.patronymic}'
        else:
            fio = f'{self.last_name} {self.first_name}'
        return fio

    # @receiver(post_save, sender=User)
    # def create_auth_token(sender, instance=None, created=False, **kwargs):
    #     if created:
    #         Token.objects.create(user=instance)

    def __str__(self) -> str:
        return self.lastname_and_initials


class NotificationAppRoute(models.Model):
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
