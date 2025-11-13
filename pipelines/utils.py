import os
import re
import sys
from datetime import date, datetime

import django
from openpyxl import load_workbook

# Настройка Django окружения
sys.path.append(r"H:\WorkDocuments\Dev\module_app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "module_app.settings")
django.setup()


from pipelines.models import Bend, Diagnostics, Pipe, Tube, TubeUnit, TubeVersion, Anomaly

# Tube.objects.all().delete()
# TubeVersion.objects.all().delete()
# TubeUnit.objects.all().delete()
# Anomaly.objects.all().delete()
# Diagnostics.objects.all().delete()
Bend.objects.all().delete()

HEADER_KEYWORDS = ["Номер трубы", "Толщина", "Тип трубы"]


def is_header(row):
    """Определяем, является ли строка заголовком таблицы."""
    row_str = " ".join([str(x) for x in row if x])
    return any(k in row_str for k in HEADER_KEYWORDS)


def extract_number_and_suffix(tube_num: str):
    """Извлекаем числовую часть и суффикс (например, 2941а → 2941, 'а')."""
    if not tube_num:
        return None, ""
    m = re.match(r"(\d+)(.*)", str(tube_num).strip())
    if not m:
        return None, ""
    return int(m.group(1)), m.group(2).strip().lower()


def parse_range(range_str: str):
    """Парсим диапазон '2941а - 5195' → (2941, 5195)."""
    parts = [p.strip() for p in range_str.split("-")]
    start, _ = extract_number_and_suffix(parts[0])
    end, _ = extract_number_and_suffix(parts[1])
    return start, end


def find_pipe_for_tube(tube_num, pipe_ranges):
    """Определяем участок (Pipe) по номеру трубы."""
    num, _ = extract_number_and_suffix(tube_num)
    if num is None:
        return None
    for pipe_id, range_str in pipe_ranges.items():
        start, end = parse_range(range_str)
        # диапазон открытый (не включаем края)
        if start < num < end:
            try:
                return Pipe.objects.get(id=pipe_id)
            except Pipe.DoesNotExist:
                print(f"⚠️ Pipe id={pipe_id} не найден")
                return None
    return None


def get_or_create_diagnostics_for_pipes(pipe_ids, start_str, end_str):
    """Создаёт (или получает) один объект Diagnostics, связанный со всеми участками."""
    start_date = datetime.strptime(start_str, "%d.%m.%Y").date()
    end_date = datetime.strptime(end_str, "%d.%m.%Y").date()

    # Пробуем найти существующую диагностику
    diagnostics = Diagnostics.objects.filter(
        start_date=start_date,
        end_date=end_date,
    ).first()

    if not diagnostics:
        # Создаём без вызова full_clean()
        diagnostics = Diagnostics.objects.create(
            start_date=start_date,
            end_date=end_date,
            description=f"Диагностика участков {', '.join(map(str, pipe_ids))} ({start_date}–{end_date})"
        )
        print(f"🧾 Создан новый объект диагностики (id={diagnostics.id})")
    else:
        print(f"ℹ️ Найдена существующая диагностика ({start_date}–{end_date}) id={diagnostics.id}")

    # Теперь безопасно добавляем участки (M2M)
    for pipe_id in pipe_ids:
        try:
            pipe = Pipe.objects.get(id=pipe_id)
            diagnostics.pipes.add(pipe)
        except Pipe.DoesNotExist:
            print(f"⚠️ Участок id={pipe_id} не найден")

    # Теперь вызываем clean(), чтобы модель прошла проверку
    diagnostics.full_clean()
    diagnostics.save()
    return diagnostics



def import_tubes(filepath, pipe_ranges: dict, diagnostics_start: str, diagnostics_end: str):
    print(f"📘 Импорт из файла: {filepath}")
    wb = load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active

    # создаём/находим диагностику, связанную со всеми участками
    diagnostics = get_or_create_diagnostics_for_pipes(pipe_ranges.keys(), diagnostics_start, diagnostics_end)

    header_found = False
    created_versions = 0
    created_tubes = 0

    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if is_header(row):
            header_found = True
            continue
        if not header_found:
            continue
        if not row[1]:  # пустая строка
            continue
        if is_header(row):  # повторная шапка
            continue

        tube_num = str(row[1]).strip()
        pipe = find_pipe_for_tube(tube_num, pipe_ranges)
        if pipe is None:
            continue

        # --- Tube ---
        tube, created = Tube.objects.get_or_create(
            pipe=pipe,
            tube_num=tube_num,
            defaults={"active": True, "installed_date": date.today()},
        )
        if created:
            created_tubes += 1

        # --- TubeVersion ---
        try:
            TubeVersion.objects.create(
                tube=tube,
                diagnostics=diagnostics,
                version_type="diagnostic",
                date=diagnostics.end_date,
                tube_length=float(row[2]) if row[2] else 0,
                thickness=float(row[3]) if row[3] else 0,
                tube_type=str(row[4]).strip() if row[4] else "without",
                yield_strength=int(row[5]) if row[5] else 0,
                tear_strength=int(row[6]) if row[6] else 0,
                category=str(row[7]).strip() if row[7] else "II",
                reliability_material=float(row[8]) if row[8] else None,
                working_conditions=float(row[9]) if row[9] else None,
                reliability_pressure=float(row[10]) if row[10] else None,
                reliability_coef=float(row[11]) if row[11] else None,
                impact_strength=float(row[12]) if row[12] else None,
                steel_grade=str(row[13]).strip() if row[13] else None,
                weld_position=str(row[14]).strip() if row[14] else None,
                from_reference_start=str(row[15]).strip() if row[15] else None,
                to_reference_end=str(row[16]).strip() if row[16] else None,
                comment=str(row[17]).strip() if row[17] else None,
            )
            created_versions += 1
        except Exception as e:
            print(f"⚠️ Ошибка в строке {i}: {e}")
            continue

    print(f"\n✅ Импорт завершён:")
    print(f"  • труб создано — {created_tubes}")
    print(f"  • версий создано — {created_versions}")
    print(f"  • диагностика ID={diagnostics.id}, диапазон {diagnostics_start}–{diagnostics_end}")


def import_tube_units(filepath):
    """
    Импорт элементов обустройства и привязка к TubeVersion последней диагностики.
    """
    print(f"📘 Импорт элементов обустройства из: {filepath}")

    try:
        diagnostics = Diagnostics.objects.latest('end_date')
    except Diagnostics.DoesNotExist:
        print("❌ Нет записей Diagnostics — невозможно выполнить импорт элементов.")
        return

    wb = load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active

    header_found = False
    created_units = 0

    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        # Пропуск мусора и шапок
        if not any(row):
            continue
        row_str = " ".join([str(x) for x in row if x])
        if any(keyword in row_str.lower() for keyword in ["тип", "одометр", "труба"]):
            header_found = True
            continue
        if not header_found:
            continue

        try:
            tube_num = str(row[1]).strip()  # предположим, в первом столбце — номер трубы
            unit_type_raw = str(row[4]).strip().lower() if row[4] else None
            odometr = float(row[0]) if row[0] else None
            description = str(row[5]).strip() if row[5] else None
            comment = str(row[7]).strip() if row[7] else None
        except Exception as e:
            print(f"⚠️ Ошибка парсинга строки {i}: {e}")
            continue

        # ищем трубу и последнюю версию
        tube = Tube.objects.filter(tube_num=tube_num).first()
        if not tube:
            print(f"⚠️ Труба {tube_num} не найдена — пропуск строки {i}")
            continue

        version = TubeVersion.objects.filter(tube=tube, diagnostics=diagnostics).order_by('-date').first()
        if not version:
            print(f"⚠️ Версия для трубы {tube_num} и диагностики {diagnostics.id} не найдена")
            continue

        # определяем тип элемента
        UNIT_TYPE_MAP = {
            "кран": "valv",
            "отвод": "offt",
            "врезка": "offt",
            "тройник": "tee",
            "эхз": "cpco",
            "окно": "wiwd",
            "футляр-начало": "casb",
            "футляр-конец": "case",
            "маркер": "mark",
            "пригруз": "anch",
            "обустройство": "pfix",
        }

        unit_type = "pfix"  # по умолчанию
        for k, v in UNIT_TYPE_MAP.items():
            if v in unit_type_raw:
                unit_type = v
                break

        # создаём элемент
        TubeUnit.objects.create(
            tube=version,
            unit_type=unit_type,
            odometr_data=odometr,
            description=description,
            comment=comment,
        )
        created_units += 1

    print(f"\n✅ Импорт элементов завершён:")
    print(f"  • создано элементов: {created_units}")
    print(f"  • диагностика: {diagnostics.id} ({diagnostics.start_date} — {diagnostics.end_date})")


def import_anomalies(filepath):
    """
    Импорт аномалий из Excel-файла и привязка их к TubeVersion последней диагностики.
    """
    ANOMALY_NATURE_MAP = {
        'Аномалия кольцевого шва': 'gwan',
        'Аномалия продольного шва': 'lwan',
        'Механическое повреждение': 'goug',
        'Коррозия': 'corr',
        'Вмятина': 'dent',
        'Гофр': 'wrin',
        'Технологический дефект': 'artd',
        'Заводской дефект': 'mian',
        'Зона продольных трещин': 'scc',
        'Трещина на продольном шве': 'lwcr',
    }

    SIZE_CLASS_MAP = {
        'Не указан': '',
        'Обширный': 'gene',
        'Каверна': 'pitt',
        'Поперечная канавка': 'cigr',
        'Продольная канавка': 'axgr',
        'Продольный паз': 'axsl',
        'Поперечный паз': 'cisl',
    }

    LOCATION_MAP = {
        'INT': 'int',
        'EXT': 'ext',
        'MID': 'mid',
        'N/A': 'n/a',
    }
    print(f"📘 Импорт аномалий из: {filepath}")

    try:
        diagnostics = Diagnostics.objects.latest('end_date')
    except Diagnostics.DoesNotExist:
        print("❌ Нет записей Diagnostics — невозможно выполнить импорт аномалий.")
        return

    wb = load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active

    header_found = False
    created_anomalies = 0

    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        # пропускаем пустые строки
        if not any(row):
            continue

        # определяем строку с заголовками
        row_str = " ".join([str(x) for x in row if x])
        if "расстояние" in row_str.lower() and "шва" in row_str.lower():
            header_found = True
            continue
        if not header_found:
            continue

        try:
            # индекс колонок по структуре файла
            distance = float(row[0]) if row[0] else None
            from_left_weld_to_max = float(row[1]) if row[1] else None
            from_left_weld_to_start = float(row[2]) if row[2] else None
            from_right_weld_to_max = float(row[3]) if row[3] else None
            from_right_weld_to_start = float(row[4]) if row[4] else None
            from_long_weld_to_start = int(row[5]) if row[5] else None
            from_long_weld_to_max = int(row[6]) if row[6] else None
            from_long_weld_to_center = int(row[7]) if row[7] else None
            min_distance_to_long_weld = int(row[8]) if row[8] else None
            min_distance_to_circ_weld = int(row[9]) if row[9] else None
            start_point_orientation = str(row[24]) if row[24] else None
            max_point_orientation = str(row[25]) if row[25] else None
            center_orientation = str(row[26]) if row[26] else None
            anomaly_description = str(row[20]) if row[20] else None

            anomaly_nature_text = str(row[18]).strip() if row[18] else None  # "Характер особенности"
            size_class_text = str(row[19]).strip() if row[19] else None      # "Класс размера"
            location_text = str(row[31]).strip() if row[31] else None        # "Расположение"

            # Преобразуем текстовые значения в ключи choices
            anomaly_nature = ANOMALY_NATURE_MAP.get(anomaly_nature_text)
            size_class = SIZE_CLASS_MAP.get(size_class_text, '')
            location = LOCATION_MAP.get(location_text)

            anomaly_length = int(row[28]) if row[28] else None
            anomaly_width = int(row[29]) if row[29] else None
            anomaly_depth = float(row[30]) if row[30] else None
            comment = str(row[32]) if row[32] else None
            tube_num = str(row[10]).strip() if row[10] else None
            safe_pressure_coefficient = float(row[38]) if row[38] else None
            danger_level = str(row[43]).strip() if len(row) > 43 and row[43] else None
        except Exception as e:
            print(f"⚠️ Ошибка парсинга строки {i}: {e}")
            continue

        if not tube_num:
            continue

        # ищем трубу и версию для текущей диагностики
        tube = Tube.objects.filter(tube_num=tube_num).first()
        if not tube:
            print(f"⚠️ Труба {tube_num} не найдена — пропуск строки {i}")
            continue

        version = TubeVersion.objects.filter(tube=tube, diagnostics=diagnostics).order_by('-date').first()
        if not version:
            print(f"⚠️ Версия для трубы {tube_num} и диагностики {diagnostics.id} не найдена")
            continue

        # создаём аномалию
        try:
            Anomaly.objects.create(
                tube=version,
                distance=distance,
                from_left_weld_to_max=from_left_weld_to_max,
                from_left_weld_to_start=from_left_weld_to_start,
                from_right_weld_to_max=from_right_weld_to_max,
                from_right_weld_to_start=from_right_weld_to_start,
                from_long_weld_to_start=from_long_weld_to_start,
                from_long_weld_to_max=from_long_weld_to_max,
                from_long_weld_to_center=from_long_weld_to_center,
                min_distance_to_long_weld=min_distance_to_long_weld,
                min_distance_to_circ_weld=min_distance_to_circ_weld,
                start_point_orientation=start_point_orientation,
                max_point_orientation=max_point_orientation,
                center_orientation=center_orientation,
                anomaly_nature=anomaly_nature,
                anomaly_description=anomaly_description,
                size_class=size_class,
                location=location,
                anomaly_length=anomaly_length,
                anomaly_width=anomaly_width,
                anomaly_depth=anomaly_depth,
                comment=comment,
                safe_pressure_coefficient=safe_pressure_coefficient,
                danger_level=danger_level,
            )
            created_anomalies += 1
        except Exception as e:
            print(f"⚠️ Ошибка создания аномалии (строка {i}): {e}")

    print(f"\n✅ Импорт аномалий завершён:")
    print(f"  • создано записей: {created_anomalies}")
    print(f"  • диагностика: {diagnostics.id} ({diagnostics.start_date} — {diagnostics.end_date})")


def import_bends(filepath):
    """
    Импорт отводов из Excel-файла и привязка их к TubeVersion последней диагностики.
    """
    # Словари для маппинга текстовых значений на ключи choices
    BEND_TYPE_MAP = {
        'Упруго-пластический изгиб': 'elastic_plastic',
        'Отвод холодного гнутья': 'cold_bend',
        'Отвод сегментный': 'segment_bend',
    }

    DIRECTION_MAP = {
        'Вертикальная': 'vertical',
        'Горизонтальная': 'horizontal',
    }

    print(f"📘 Импорт отводов из: {filepath}")

    try:
        diagnostics = Diagnostics.objects.latest('end_date')
    except Diagnostics.DoesNotExist:
        print("❌ Нет записей Diagnostics — невозможно выполнить импорт отводов.")
        return

    wb = load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active

    header_found = False
    created_bends = 0

    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        # пропускаем пустые строки
        if not any(row):
            continue

        # определяем строку с заголовками
        row_str = " ".join([str(x) for x in row if x])
        if "начало" in row_str.lower() and "конец" in row_str.lower() and "номер трубы" in row_str.lower():
            header_found = True
            continue
        if not header_found:
            continue

        try:
            # индекс колонок по структуре файла
            start_point = float(row[0]) if row[0] else None
            end_point = float(row[1]) if row[1] else None
            tube_num = str(row[2]).strip() if row[2] else None
            segment_count = int(row[3]) if row[3] else None
            radius = float(row[4]) if row[4] else None
            bend_angle = float(row[5]) if row[5] else None
            projection_angle = str(row[6]) if row[6] else None

            # Поля choices - маппинг текста на ключи
            bend_type_text = str(row[7]).strip() if row[7] else None  # "Тип"
            direction_text = str(row[8]).strip() if row[8] else None  # "Направление"

            # Преобразуем текстовые значения в ключи choices
            bend_type = BEND_TYPE_MAP.get(bend_type_text)
            direction = DIRECTION_MAP.get(direction_text)

            # anomaly_count = int(row[10]) if row[10] else 0
            comment = str(row[10]) if row[10] else None

            # Географические координаты (если есть в данных)
            latitude = float(row[11]) if len(row) > 11 and row[11] else None
            longitude = float(row[12]) if len(row) > 12 and row[12] else None
            altitude = float(row[13]) if len(row) > 13 and row[13] else None

            # Статус безопасности
            safety_status = str(row[14]) if len(row) > 14 and row[14] else None

        except Exception as e:
            print(f"⚠️ Ошибка парсинга строки {i}: {e}")
            continue

        if not tube_num or not start_point or not end_point:
            print(f"⚠️ Пропуск строки {i}: отсутствуют обязательные данные (труба, начало, конец)")
            continue

        # ищем трубу и версию для текущей диагностики
        tube = Tube.objects.filter(tube_num=tube_num).first()
        if not tube:
            print(f"⚠️ Труба {tube_num} не найдена — пропуск строки {i}")
            continue

        version = TubeVersion.objects.filter(tube=tube, diagnostics=diagnostics).order_by('-date').first()
        if not version:
            print(f"⚠️ Версия для трубы {tube_num} и диагностики {diagnostics.id} не найдена")
            continue

        # создаём отвод
        try:
            bend = Bend.objects.create(
                tube=version,
                start_point=start_point,
                end_point=end_point,
                tube_number=tube_num,
                segment_count=segment_count,
                radius=radius,
                bend_angle=bend_angle,
                projection_angle=projection_angle,
                bend_type=bend_type,
                direction=direction,
                comment=comment,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                safety_status=safety_status,
            )

            # Вызываем save для автоматического вычисления radius_in_diameters и парсинга комментария
            bend.save()

            created_bends += 1

            # Отладочная информация для первых нескольких записей
            if created_bends <= 5:
                print(f"✅ Создан отвод: труба {tube_num}, тип: {bend_type_text} -> {bend_type}, направление: {direction_text} -> {direction}")

        except Exception as e:
            print(f"⚠️ Ошибка создания отвода (строка {i}): {e}")
            print(f"   Параметры: type={bend_type}, direction={direction}")

    print(f"\n✅ Импорт отводов завершён:")
    print(f"  • создано записей: {created_bends}")
    print(f"  • диагностика: {diagnostics.id} ({diagnostics.start_date} — {diagnostics.end_date})")


if __name__ == "__main__":
    pipe_ranges = {
        14: "2941а - 5195",
        15: "5195 - 7480",
        16: "7480 - 7600",
    }
    diagnostics_start = '04.04.2025'
    diagnostics_end = '07.04.2025'
    filepath = r"H:\WorkDocuments\Dev\module_app\fixtures\data\nord_uc_2.xlsx"
    filepath_units = r"H:\WorkDocuments\Dev\module_app\fixtures\data\tubeunits_nord_uc_2.xlsx"
    filepath_anomalies = r"H:\WorkDocuments\Dev\module_app\fixtures\data\anomalies_nord_uc_2.xlsx"
    filepath_bends = r"H:\WorkDocuments\Dev\module_app\fixtures\data\bends_nord_uc_2.xlsx"
    # import_tubes(filepath, pipe_ranges, diagnostics_start, diagnostics_end)
    # import_tube_units(filepath_units)
    # import_anomalies(filepath_anomalies)
    import_bends(filepath_bends)
