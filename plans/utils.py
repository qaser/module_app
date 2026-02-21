import datetime as dt

from dateutil.relativedelta import relativedelta
from plans.models import EventInstance, EventStatus, Report, ReportStatus
from django.utils import timezone


def recalc_event_instance_status(instance: EventInstance):
    statuses = instance.completions.values_list('status', flat=True)
    if not statuses:
        return
    if all(s == EventStatus.COMPLETED for s in statuses):
        instance.status = EventStatus.COMPLETED
        instance.completed_at = timezone.now().date()
        instance.is_active = False
    elif EventStatus.OVERDUE in statuses:
        instance.status = EventStatus.OVERDUE
    elif EventStatus.DELAYED in statuses:
        instance.status = EventStatus.DELAYED
    elif EventStatus.IN_WORK in statuses:
        instance.status = EventStatus.IN_WORK
    else:
        instance.status = EventStatus.NOT_STARTED
    instance.save(update_fields=['status', 'completed_at'])


# def calculate_next_due_date(event, schedule):
#     """
#     Рассчитывает СЛЕДУЮЩИЙ контрольный срок мероприятия.

#     Ключевые правила:
#     - вызывается только после выполнения мероприятия
#     - просрочка НЕ влияет на расчёт
#     - база расчёта — предыдущий event.due_date
#     """
#     if not event.due_date:
#         raise ValueError('Невозможно вычислить следующий срок без due_date')

#     base_date = event.due_date

#     # === одноразовое мероприятие ===
#     if schedule.schedule_type == 'once':
#         return None  # больше сроков нет

#     # === постоянно ===
#     if schedule.schedule_type == 'continuous':
#         # контрольная точка = следующий месяц
#         return base_date + relativedelta(months=+1)

#     # === периодическое ===
#     if schedule.schedule_type == 'periodic':
#         interval = schedule.period_interval or 1

#         if schedule.period_unit == 'week':
#             return base_date + dt.timedelta(weeks=interval)

#         if schedule.period_unit == 'month':
#             return base_date + relativedelta(months=+interval)

#         if schedule.period_unit == 'quarter':
#             return base_date + relativedelta(months=+(3 * interval))

#         if schedule.period_unit == 'year':
#             return base_date + relativedelta(years=+interval)

#         raise ValueError(f'Неизвестный period_unit: {schedule.period_unit}')

#     # === относительное ===
#     if schedule.schedule_type == 'relative':
#         if not schedule.relative_base or schedule.relative_day is None:
#             raise ValueError('Для relative требуется relative_base и relative_day')

#         # --- определяем новую опорную дату ---
#         if schedule.relative_base == 'document_date':
#             ref_date = base_date

#         elif schedule.relative_base == 'month_end':
#             ref_date = base_date.replace(day=1) + relativedelta(months=+1, days=-1)

#         elif schedule.relative_base == 'quarter_end':
#             month = ((base_date.month - 1) // 3 + 1) * 3
#             ref_date = dt.date(base_date.year, month, 1) + relativedelta(months=+1, days=-1)

#         elif schedule.relative_base == 'period_end':
#             ref_date = base_date.replace(day=1) + relativedelta(months=+1, days=-1)

#         else:
#             raise ValueError(f'Неизвестный relative_base: {schedule.relative_base}')

#         # --- применяем смещение ---
#         if schedule.relative_position == 'before':
#             return ref_date.replace(day=min(schedule.relative_day, ref_date.day))

#         if schedule.relative_position == 'after':
#             return ref_date + dt.timedelta(days=schedule.relative_day)

#         raise ValueError(f'Неизвестный relative_position: {schedule.relative_position}')

#     raise ValueError(f'Неизвестный schedule_type: {schedule.schedule_type}')


# def calculate_due_date(event, schedule):
#     """
#     Рассчитывает ПЕРВЫЙ контрольный срок мероприятия
#     на основании EventSchedule.

#     Условия:
#     - только календарные дни
#     - точка отсчёта — дата создания мероприятия
#     """

#     # 1️⃣ Базовая дата — день создания мероприятия
#     if hasattr(event, 'created_at') and event.created_at:
#         base_date = event.created_at.date()
#     else:
#         base_date = timezone.now().date()

#     # 2️⃣ Тип: конкретная дата
#     if schedule.schedule_type == 'once':
#         # relative_day трактуется как смещение в днях от даты создания
#         if schedule.relative_day is None:
#             raise ValueError('Для schedule_type="once" требуется relative_day')
#         return base_date + dt.timedelta(days=schedule.relative_day)

#     # 3️⃣ Тип: постоянно
#     if schedule.schedule_type == 'continuous':
#         # Постоянные задачи ВСЕГДА имеют контрольную точку
#         # Берём первый контрольный период
#         return base_date + relativedelta(months=+1)

#     # 4️⃣ Тип: периодическое
#     if schedule.schedule_type == 'periodic':
#         if not schedule.period_unit:
#             raise ValueError('Для periodic требуется period_unit')

#         interval = schedule.period_interval or 1

#         if schedule.period_unit == 'week':
#             return base_date + dt.timedelta(weeks=interval)

#         if schedule.period_unit == 'month':
#             return base_date + relativedelta(months=+interval)

#         if schedule.period_unit == 'quarter':
#             return base_date + relativedelta(months=+(3 * interval))

#         if schedule.period_unit == 'year':
#             return base_date + relativedelta(years=+interval)

#         raise ValueError(f'Неизвестный period_unit: {schedule.period_unit}')

#     # 5️⃣ Тип: относительное
#     if schedule.schedule_type == 'relative':
#         if not schedule.relative_base or schedule.relative_day is None:
#             raise ValueError('Для relative требуется relative_base и relative_day')

#         # --- определяем опорную дату ---
#         if schedule.relative_base == 'document_date':
#             ref_date = base_date

#         elif schedule.relative_base == 'month_end':
#             ref_date = base_date.replace(day=1) + relativedelta(months=+1, days=-1)

#         elif schedule.relative_base == 'quarter_end':
#             month = ((base_date.month - 1) // 3 + 1) * 3
#             ref_date = dt.date(base_date.year, month, 1) + relativedelta(months=+1, days=-1)

#         elif schedule.relative_base == 'period_end':
#             # трактуем как конец месяца
#             ref_date = base_date.replace(day=1) + relativedelta(months=+1, days=-1)

#         else:
#             raise ValueError(f'Неизвестный relative_base: {schedule.relative_base}')

#         # --- применяем смещение ---
#         if schedule.relative_position == 'before':
#             return ref_date.replace(day=min(schedule.relative_day, ref_date.day))

#         if schedule.relative_position == 'after':
#             return ref_date + dt.timedelta(days=schedule.relative_day)

#         raise ValueError(f'Неизвестный relative_position: {schedule.relative_position}')

#     raise ValueError(f'Неизвестный schedule_type: {schedule.schedule_type}')


# def update_protocol_completion_status(activity):
#     """
#     Проверяет, все ли мероприятия протокола имеют статус 'completed'.
#     Если все — ставит is_complete = True, иначе — False.
#     """
#     protocol = activity.protocol
#     total_activities = protocol.activities.filter(is_archived=False).count()
#     if total_activities == 0:
#         # Если нет активных мероприятий — считаем протокол "выполненным"
#         protocol.is_complete = True
#     else:
#         completed_count = protocol.activities.filter(
#             is_archived=False,
#             status='completed'
#         ).count()
#         protocol.is_complete = (completed_count == total_activities)
#     protocol.save(update_fields=['is_complete'])


# def update_order_completion_status(activity):
#     """
#     Проверяет, все ли мероприятия приказа имеют статус 'completed'.
#     Если все — ставит is_complete = True, иначе — False.
#     """
#     order = activity.order
#     total_activities = order.activities.filter(is_archived=False).count()
#     if total_activities == 0:
#         # Если нет активных мероприятий — считаем протокол "выполненным"
#         order.is_complete = True
#     else:
#         completed_count = order.activities.filter(
#             is_archived=False,
#             status='completed'
#         ).count()
#         order.is_complete = (completed_count == total_activities)
#     order.save(update_fields=['is_complete'])


# def update_activity_status(activity):
#     departments = set(activity.departments.all())
#     responsibilities = {resp.department: resp for resp in activity.responsibilities.all()}
#     if not departments:
#         return
#     # Переменные для расчёта
#     all_completed = True
#     has_overdue = False
#     has_approaching = False
#     latest_completion_date = None  # Для хранения самой поздней даты завершения
#     # --- Обработка для всех типов мероприятий ---
#     for dept in departments:
#         resp = responsibilities.get(dept)
#         if resp:
#             # Собираем статусы
#             if resp.status != 'completed':
#                 all_completed = False
#             if resp.status == 'overdue':
#                 has_overdue = True
#             elif resp.status == 'approaching_deadline':
#                 has_approaching = True
#             # Учитываем actual_completion_date только если она указана и валидна
#             if resp.actual_completion_date and resp.status in ('completed', 'mark'):
#                 if latest_completion_date is None or resp.actual_completion_date > latest_completion_date:
#                     latest_completion_date = resp.actual_completion_date
#         else:
#             all_completed = False  # Нет отчёта → не выполнено
#     # --- Обновление actual_completion_date (только для 'date') ---
#     if activity.deadline_type == 'date':
#         # Сохраняем самую позднюю дату завершения среди подразделений
#         if latest_completion_date:
#             # Защита от будущих дат
#             if latest_completion_date <= dt.date.today():
#                 activity.actual_completion_date = latest_completion_date
#             else:
#                 activity.actual_completion_date = dt.date.today()
#         else:
#             pass
#     else:
#         activity.actual_completion_date = None

#     if activity.deadline_type in ('periodic', 'permanent'):
#         new_status = 'overdue' if has_overdue else 'approaching_deadline' if has_approaching else 'open'
#     else:  # deadline_type == 'date'
#         new_status = 'completed' if all_completed else 'overdue' if has_overdue else 'approaching_deadline' if has_approaching else 'open'
#     fields_to_update = ['last_status_check']
#     if activity.status != new_status:
#         activity.status = new_status
#         fields_to_update.append('status')
#     if 'actual_completion_date' not in fields_to_update:
#         old_date = activity.actual_completion_date
#         fields_to_update.append('actual_completion_date')
#     activity.save(update_fields=fields_to_update)


# class ReportScheduler:

#     @staticmethod
#     def is_working_day(date):
#         """Проверка, является ли день рабочим (без учета праздников)"""
#         # В субботу (5) и воскресенье (6) - выходные
#         return date.weekday() < 5

#     @staticmethod
#     def add_working_days(start_date, days_to_add):
#         """Добавляет указанное количество рабочих дней к дате"""
#         current_date = start_date
#         days_added = 0
#         while days_added < abs(days_to_add):
#             if days_to_add > 0:
#                 current_date += dt.timedelta(days=1)
#             else:
#                 current_date -= dt.timedelta(days=1)
#             if ReportScheduler.is_working_day(current_date):
#                 days_added += 1
#         return current_date

#     def calculate_next_due_date(self, report, last_completed_date=None):
#         """Рассчитывает следующую дату сдачи отчета"""
#         today = dt.date.today()
#         if report.frequency == 'continuous':
#             # Постоянные отчеты - всегда "В работе"
#             return None
#         elif report.frequency == 'once':
#             # Единоразовые отчеты
#             if report.order_date:
#                 return report.order_date
#             return today
#         elif report.frequency == 'daily':
#             # Ежедневные отчеты - следующий рабочий день
#             return self.add_working_days(today, 1)
#         elif report.frequency == 'weekly':
#             # Еженедельные отчеты
#             schedule = report.schedules.first()
#             day = schedule.day_of_week if schedule else 0  # Понедельник по умолчанию
#             # Находим следующий указанный день недели
#             days_ahead = day - today.weekday()
#             if days_ahead <= 0:
#                 days_ahead += 7
#             return today + dt.timedelta(days=days_ahead)
#         elif report.frequency == 'monthly':
#             # Ежемесячные отчеты
#             schedule = report.schedules.first()
#             if schedule and schedule.days_before_end_of_month:
#                 # Случай "до 3 числа месяца" - значит, отчет за предыдущий месяц
#                 # Определяем последний день текущего месяца
#                 next_month = today.replace(day=1) + relativedelta(months=1)
#                 due_date = next_month - dt.timedelta(days=1)  # Последний день месяца
#                 # Возвращаемся на указанное количество рабочих дней
#                 return self.add_working_days(due_date, -schedule.days_before_end_of_month)
#             elif schedule and schedule.day_of_month:
#                 # Конкретный день месяца
#                 day = schedule.day_of_month
#                 next_month = today.replace(day=1) + relativedelta(months=1)
#                 # Проверяем, существует ли указанный день в месяце
#                 try:
#                     return next_month.replace(day=min(day, 28))  # Безопасное значение
#                 except ValueError:
#                     # Если день не существует (например, 31 февраля), берем последний день месяца
#                     return next_month - dt.timedelta(days=1)
#             else:
#                 # По умолчанию - 1 число следующего месяца
#                 next_month = today.replace(day=1) + relativedelta(months=1)
#                 return next_month.replace(day=1)
#         elif report.frequency == 'quarterly':
#             # Ежеквартальные отчеты
#             schedule = report.schedules.first()
#             current_month = today.month
#             # Определяем текущий квартал
#             current_quarter = (current_month - 1) // 3 + 1
#             # Определяем месяц окончания квартала
#             quarter_end_month = current_quarter * 3
#             # Определяем дату окончания квартала
#             if current_month == quarter_end_month:
#                 # Если текущий месяц - конец квартала
#                 due_date = today.replace(day=1) + relativedelta(months=1)  # 1 число следующего месяца
#             else:
#                 # Иначе - последний день текущего квартала
#                 if quarter_end_month > 12:
#                     quarter_end_month = 12
#                     year = today.year + 1
#                 else:
#                     year = today.year
#                 # Определяем последний день квартала
#                 next_quarter_start = dt.date(year, quarter_end_month, 1) + relativedelta(months=1)
#                 due_date = next_quarter_start - dt.timedelta(days=1)
#             # Применяем смещение дней, если указано
#             if schedule and schedule.days_after_trigger:
#                 return self.add_working_days(due_date, schedule.days_after_trigger)
#             return due_date
#         elif report.frequency == 'yearly':
#             # Ежегодные отчеты
#             schedule = report.schedules.first()
#             if schedule and schedule.month_of_year:
#                 month = schedule.month_of_year
#                 year = today.year
#                 # Если текущий месяц уже прошел указанный месяц отчетности
#                 if today.month > month:
#                     year += 1
#                 return dt.date(year, month, 1)
#             else:
#                 # По умолчанию - 1 января следующего года
#                 return dt.date(today.year + 1, 1, 1)
#         elif report.frequency == 'custom':
#             # Особая периодичность
#             return self.parse_custom_frequency(report)
#         return today

#     def parse_custom_frequency(self, report):
#         """Парсит специальные условия периодичности"""
#         if not report.custom_frequency_description:
#             return dt.date.today() + dt.timedelta(days=7)
#         desc = report.custom_frequency_description.lower()
#         # Пример: "в течение 3 рабочих дней после оформления документации"
#         if 'в течение' in desc and 'рабочих дней' in desc:
#             # Ищем количество дней
#             import re
#             match = re.search(r'(\d+)\s*рабочих дней', desc)
#             if match:
#                 days = int(match.group(1))
#                 # Для примера, считаем что триггер - сегодня
#                 return self.add_working_days(
#                     dt.date.today(),
#                     days
#                 )
#         # Пример: "до 3 числа месяца"
#         if 'до' in desc and 'числа' in desc and 'месяца' in desc:
#             match = re.search(r'до\s*(\d+)\s*числа', desc)
#             if match:
#                 day = int(match.group(1))
#                 # Отчет за предыдущий месяц, сдача до X числа текущего
#                 today = dt.date.today()
#                 return today.replace(day=min(day, 28))
#         # Пример: "не позднее 5 рабочих дней после окончания квартала"
#         if 'не позднее' in desc and 'рабочих дней после окончания квартала' in desc:
#             match = re.search(r'не позднее\s*(\d+)\s*рабочих дней', desc)
#             if match:
#                 days = int(match.group(1))
#                 # Определяем конец текущего квартала
#                 today = dt.date.today()
#                 current_quarter = (today.month - 1) // 3 + 1
#                 quarter_end_month = current_quarter * 3
#                 if quarter_end_month > 12:
#                     quarter_end_month = 12
#                     year = today.year + 1
#                 else:
#                     year = today.year
#                 # Последний день квартала
#                 quarter_end = dt.date(year, quarter_end_month, 1) + relativedelta(months=1) - dt.timedelta(days=1)
#                 # Добавляем рабочие дни после конца квартала
#                 return self.add_working_days(quarter_end, days)
#         return dt.date.today() + dt.timedelta(days=7)

#     def create_periodic_statuses(self):
#         """Создает статусы для отчетов по их периодичности"""
#         today = dt.date.today()
#         reports = Report.objects.filter(is_active=True)
#         for report in reports:
#             # Для постоянных отчетов создаем один статус
#             if report.frequency == 'continuous':
#                 ReportStatus.objects.get_or_create(
#                     report=report,
#                     period_start=today.replace(day=1),
#                     defaults={
#                         'status': 'in_work',
#                         'due_date': None  # Нет срока для постоянных отчетов
#                     }
#                 )
#                 continue
#             due_date = self.calculate_next_due_date(report)
#             if not due_date:
#                 continue
#             # Определяем период отчета
#             period_start = self.get_period_start(report, due_date)
#             period_end = self.get_period_end(report, period_start)
#             # Проверяем, существует ли уже статус на этот период
#             status_exists = ReportStatus.objects.filter(
#                 report=report,
#                 period_start=period_start,
#                 period_end=period_end
#             ).exists()
#             if not status_exists:
#                 ReportStatus.objects.create(
#                     report=report,
#                     period_start=period_start,
#                     period_end=period_end,
#                     due_date=due_date,
#                     status='pending'
#                 )

#     def get_period_start(self, report, due_date):
#         """Определяет начало отчетного периода"""
#         if report.frequency == 'weekly':
#             # Неделя начинается за 7 дней до сдачи
#             return due_date - dt.timedelta(days=7)
#         elif report.frequency == 'monthly':
#             # Месяц начинается 1-го числа месяца сдачи
#             return due_date.replace(day=1)
#         elif report.frequency == 'quarterly':
#             # Квартал начинается с начала квартала
#             quarter_start_month = ((due_date.month - 1) // 3) * 3 + 1
#             return due_date.replace(month=quarter_start_month, day=1)
#         elif report.frequency == 'yearly':
#             # Год начинается 1 января
#             return due_date.replace(month=1, day=1)
#         # Для остальных частот период начинается сегодня
#         return dt.date.today().replace(day=1)

#     def get_period_end(self, report, period_start):
#         """Определяет конец отчетного периода"""
#         if report.frequency == 'weekly':
#             return period_start + dt.timedelta(days=6)
#         elif report.frequency == 'monthly':
#             return period_start + relativedelta(months=1) - dt.timedelta(days=1)
#         elif report.frequency == 'quarterly':
#             return period_start + relativedelta(months=3) - dt.timedelta(days=1)
#         elif report.frequency == 'yearly':
#             return period_start.replace(year=period_start.year + 1) - dt.timedelta(days=1)
#         # Для остальных частот период заканчивается в день сдачи
#         return period_start
