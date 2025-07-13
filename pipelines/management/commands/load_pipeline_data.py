import datetime
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from pipelines.models import Anomaly, Diagnostics, Pipe, Tube


class Command(BaseCommand):
    help = 'Генерирует тестовые данные: Tube, Anomaly'

    def handle(self, *args, **kwargs):
        Tube.objects.all().delete()
        Anomaly.objects.all().delete()
        total_tubes_per_pipe = 3000
        anomaly_total = 100
        anomaly_diagnostics_id = 1

        # Получаем диагностическую запись (если нет — пропускаем генерацию аномалий)
        try:
            diagnostics = Diagnostics.objects.get(id=anomaly_diagnostics_id)
        except Diagnostics.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'Diagnostics с id={anomaly_diagnostics_id} не найден. Аномалии не будут созданы.'))
            diagnostics = None

        for pipe_id in range(1, 62):  # от 1 до 61 включительно
            try:
                pipe = Pipe.objects.get(id=pipe_id)
            except Pipe.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Pipe с id={pipe_id} не найден. Пропускаем.'))
                continue

            self.stdout.write(f'Генерация труб для участка {pipe_id}...')

            tubes_to_create = []
            for i in range(1, total_tubes_per_pipe + 1):
                tube = Tube(
                    pipe=pipe,
                    tube_num=i,
                    tube_length=round(random.uniform(10.4, 11.9), 2),
                    thickness=18.4,
                    seam_num=random.choice([1, 2])
                )
                tubes_to_create.append(tube)

            # bulk_create возвращает список, начиная с Django 4.2 (с опцией `returning`)
            created_tubes = Tube.objects.bulk_create(tubes_to_create, batch_size=500)

            self.stdout.write(self.style.SUCCESS(f'Создано {len(created_tubes)} труб для pipe {pipe_id}.'))

            # Генерация аномалий только для pipe с id=2
            if pipe_id == 2 and diagnostics:
                self.stdout.write('Генерация аномалий...')

                anomaly_nature_choices = [choice[0] for choice in Anomaly.ANOMALY_NATURE]
                anomaly_type_choices = [choice[0] for choice in Anomaly.ANOMALY_TYPE]

                # Распределим случайно 100 аномалий по трубам
                anomalies_to_create = []
                for anomaly_num in range(1, anomaly_total + 1):
                    tube = random.choice(created_tubes)
                    anomaly = Anomaly(
                        diagnostics=diagnostics,
                        anomaly_num=anomaly_num,
                        anomaly_nature=random.choice(anomaly_nature_choices),
                        anomaly_type=random.choice(anomaly_type_choices),
                        tube=tube,
                        anomaly_length=random.randint(5, 100),
                        anomaly_width=random.randint(5, 100),
                        anomaly_depth=random.randint(1, 5),
                    )
                    anomalies_to_create.append(anomaly)

                Anomaly.objects.bulk_create(anomalies_to_create, batch_size=100)
                self.stdout.write(self.style.SUCCESS(f'Создано {len(anomalies_to_create)} аномалий для труб pipe id=2.'))

        self.stdout.write(self.style.SUCCESS('Генерация завершена.'))
