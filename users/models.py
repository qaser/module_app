from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from rest_framework.authtoken.models import Token

from locations.models import Department, Station

'''
перед миграцией необходимо закомментировать поля station.
Затем раскомментировать и снова сделать миграцию
'''

User = get_user_model()


class Role(models.TextChoices):
    ADMIN = 'admin'  # всемогущий
    MANAGER = 'manager'  # руководитель
    LEAD = 'lead'  # начальник цеха
    ENGINEER = 'engineer'  # инженер, мастер
    EMPLOYEE = 'employee'  # работник


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    patronymic = models.CharField(
        'Отчество',
        max_length=50,
        blank=True,
        null=True,
    )
    job_position = models.TextField('Должность', blank=True, null=True)
    station = models.ForeignKey(
        Station,
        verbose_name='Место работы',
        on_delete=models.CASCADE,
        related_name='user_station',
        null=True
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=30,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'

    # представление пользователя в виде Фамилия И.О.
    # с учетом отсутствия Отчества
    @property
    def lastname_and_initials(self):
        lastname = self.user.last_name
        initial_name = self.user.first_name[0]
        if self.patronymic is not None:
            initial_patronymic = self.patronymic[0]
            lastname_and_initials = (f'{lastname} '
                                     f'{initial_name}.{initial_patronymic}.')
        else:
            lastname_and_initials = f'{lastname} {initial_name}.'
        return lastname_and_initials

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    # @receiver(post_save, sender=User)
    # def create_auth_token(sender, instance=None, created=False, **kwargs):
    #     if created:
    #         Token.objects.create(user=instance)

    def __str__(self) -> str:
        return self.user.get_full_name()


class UserDepartment(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='user_dep',
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Подразделение',
        on_delete=models.CASCADE,
        related_name='dep_user'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'место работы пользователя'
        verbose_name_plural = 'места работы пользователя'

    def __str__(self) -> str:
        return self.user.get_full_name()
