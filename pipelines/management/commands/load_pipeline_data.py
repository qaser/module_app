import datetime
import random

from django.core.management.base import BaseCommand

from equipments.models import Department, Equipment
from pipelines.models import Node, NodeState, Pipe, PipeDepartment, PipeLimit, Pipeline, PipeState
from tpa.models import Factory, Valve
from users.models import ModuleUser


class Command(BaseCommand):
    help = 'Генерирует тестовые данные: Pipeline, Pipe, Node, Valve, Equipment, состояния'

    def handle(self, *args, **kwargs):
        self.stdout.write('Очистка старых данных...')
        PipeState.objects.all().delete()
        Node.objects.all().delete()
        NodeState.objects.all().delete()
        Pipe.objects.all().delete()
        # Pipeline.objects.all().delete()
        Valve.objects.all().delete()
        # PipeDepartment.objects.all().delete()
        PipeLimit.objects.all().delete()
        # Equipment.objects.all().delete()
        # Department.objects.filter(name="Цех эксплуатации №1").delete()

        # self.stdout.write('Генерация тестовых данных...')

        # cities = [
        #     ("Москва", "Казань"), ("Пермь", "Екатеринбург"), ("Уфа", "Самара"),
        #     ("Тюмень", "Сургут"), ("Краснодар", "Ростов"), ("Омск", "Новосибирск"),
        #     ("Челябинск", "Оренбург"), ("Иркутск", "Улан-Удэ"), ("Хабаровск", "Владивосток"),
        #     ("Нижний Новгород", "Киров")
        # ]

        # factory, _ = Factory.objects.get_or_create(name="Армапром", country="Россия")
        # department, _ = Department.objects.get_or_create(name="Превосходное ЛПУМГ")
        # user = ModuleUser.objects.first()

        # for i, (city1, city2) in enumerate(cities, start=1):
        #     pipeline = Pipeline.objects.create(
        #         title=f"{city1} - {city2}",
        #         order=i,
        #         description=f"Междугородний трубопровод №{i}"
        #     )
        #     self.stdout.write(f"Создан газопровод: {pipeline.title}")

        #     pipe_lengths = [30.0, 30.0, 1.5, 1.5, 30.0, 30.0]
        #     pipes = []
        #     start_km = 0.0

        #     for j, length in enumerate(pipe_lengths, start=1):
        #         pipe = Pipe.objects.create(
        #             pipeline=pipeline,
        #             department=department,
        #             start_point=start_km,
        #             end_point=start_km + length,
        #             diameter=random.choice([500, 700, 800, 1000])
        #         )
        #         start_km += length
        #         pipes.append(pipe)
        #         self.stdout.write(f" - Участок {j}: {pipe.start_point}–{pipe.end_point} км")

        #         # Добавление PipeState
        #         PipeState.objects.create(
        #             pipe=pipe,
        #             state_type='operation',
        #             current_pressure=5.0 + random.random(),
        #             is_limited=random.choice([False, False, True]),
        #             pressure_limit=6.3,
        #             limit_reason="Плановое ограничение",
        #             description="Автосоздание состояния",
        #             created_by=user
        #         )

        #     # Узлы valve
        #     valve_points = [pipes[0].start_point] + [p.end_point for p in pipes]
        #     valve_nodes = []

        #     for point in valve_points:
        #         eq = Equipment.objects.create(name=f"Кран на {point:.1f} км")
        #         eq.departments.add(department)

        #         node = Node.objects.create(
        #             node_type='valve',
        #             pipeline=pipeline,
        #             location_point=point,
        #             equipment=eq
        #         )
        #         valve_nodes.append(node)

        #         valve = Valve.objects.create(
        #             equipment=eq,
        #             title="Клапан линейный",
        #             diameter=random.choice([500, 700, 800, 1000]),
        #             pressure=16,
        #             valve_type="Кран шаровой",
        #             factory=factory,
        #             tech_number=f"V{i}{int(point*100)}",
        #             remote="Нет",
        #             design="Подземное"
        #         )

        #         # Добавление ValveState
        #         ValveState.objects.create(
        #             valve=valve,
        #             state=random.choice(['open', 'closed']),
        #             comment="Автосоздание состояния",
        #             changed_by=user
        #         )

        #         self.stdout.write(f"   + Valve @ {point} км (тех.№ {valve.tech_number})")

        #     # Host node
        #     host_point = pipes[2].end_point
        #     host_eq = Equipment.objects.create(name=f"Хост на {host_point:.1f} км")
        #     host_eq.departments.add(department)
        #     Node.objects.create(
        #         node_type='host',
        #         pipeline=pipeline,
        #         location_point=host_point,
        #         equipment=host_eq
        #     )
        #     self.stdout.write(f"   + Host узел @ {host_point} км")

        #     # Bridge nodes
        #     for v_node in valve_nodes:
        #         for offset in [-0.1, 0.1]:
        #             p = v_node.location_point + offset
        #             if pipes[0].start_point <= p <= pipes[-1].end_point:
        #                 bridge_eq = Equipment.objects.create(name=f"Перемычка @ {p:.1f} км")
        #                 bridge_eq.departments.add(department)
        #                 Node.objects.create(
        #                     node_type='bridge',
        #                     pipeline=pipeline,
        #                     location_point=p,
        #                     equipment=bridge_eq
        #                 )
        #                 self.stdout.write(f"     + Bridge узел @ {p:.1f} км")

        # self.stdout.write(self.style.SUCCESS('Генерация завершена успешно.'))
