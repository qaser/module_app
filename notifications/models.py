from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from users.models import ModuleUser, UserAppRoute


class Notification(models.Model):
    class AppChoices(models.TextChoices):
        RATIONAL = 'rational', 'Рацпредложения'
        LEAKS = 'leaks', 'Утечки газа'
        EQUIPMENT = 'equipment', 'Оборудование'
        PIPELINES = 'pipelines', 'Магистральные газопроводы'
        VALVES = 'tpa', 'Техническое обслуживание ТПА'

    user = models.ForeignKey(
        ModuleUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    app_name = models.CharField(
        'Приложение',
        max_length=20,
        choices=AppChoices.choices
    )
    object_id = models.PositiveIntegerField('ID объекта')
    title = models.CharField('Заголовок', max_length=100)
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)
    status = models.CharField('Статус', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} для {self.user}'

    def get_absolute_url(self):
        """Возвращает URL для перехода к объекту уведомления"""
        url_mapping = {
            self.AppChoices.RATIONAL: {
                'view_name': 'rational:single_proposal',
                'arg_name': 'proposal_id'
            },
            self.AppChoices.LEAKS: {
                'view_name': 'leaks:single_leak',
                'arg_name': 'leak_id'
            },
        }

        if self.app_name in url_mapping:
            try:
                return reverse(
                    url_mapping[self.app_name]['view_name'],
                    kwargs={url_mapping[self.app_name]['arg_name']: self.object_id}
                )
            except NoReverseMatch:
                print(f"URL not found for: {self.app_name} with id {self.object_id}")

        try:
            admin_url = reverse(
                f'admin:{self.app_name}_{self.app_name.lower()}_change',
                args=[self.object_id]
            )
            return admin_url
        except NoReverseMatch:
            return '#'
