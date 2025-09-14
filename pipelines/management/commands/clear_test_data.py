from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction

class Command(BaseCommand):
    help = "Полностью очищает данные во всех моделях из заданного списка приложений"

    # список приложений, которые нужно очищать
    APP_LABELS = [
        "users",
        "equipments",
        "rational",
        "pipelines",
        # "leaks",
        # добавь сюда остальные
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Не спрашивать подтверждения",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        noinput = options["noinput"]

        if not noinput:
            confirm = input(
                f"⚠️ Это удалит ВСЕ данные в приложениях: {', '.join(self.APP_LABELS)}. Продолжить? (y/N): "
            )
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Операция отменена"))
                return

        for app_label in self.APP_LABELS:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError:
                self.stdout.write(self.style.ERROR(f"Приложение '{app_label}' не найдено"))
                continue

            # удаляем модели в обратном порядке (ForeignKey зависящие модели чистятся первыми)
            models = list(app_config.get_models())[::-1]

            for model in models:
                deleted, _ = model.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f"{app_label}.{model.__name__}: удалено {deleted} объектов")
                )

        self.stdout.write(self.style.SUCCESS("✅ Очистка завершена"))
