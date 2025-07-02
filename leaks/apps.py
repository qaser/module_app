from django.apps import AppConfig


class LeaksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaks'
    verbose_name = 'Модуль "Утечки газа"'
