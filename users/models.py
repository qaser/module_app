from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from rest_framework.authtoken.models import Token

from equipments.models import Equipment


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
    equipment = models.ForeignKey(
        Equipment,
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

    # @receiver(post_save, sender=User)
    # def create_auth_token(sender, instance=None, created=False, **kwargs):
    #     if created:
    #         Token.objects.create(user=instance)

    def __str__(self) -> str:
        return self.get_full_name()
