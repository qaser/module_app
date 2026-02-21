from django.apps import AppConfig


class PlansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plans'
    verbose_name = 'Модуль "Планёрка"'

    def ready(self):
        import plans.signals
