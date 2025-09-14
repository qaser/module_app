import sys
import os
import re
import django
from openpyxl import load_workbook

# Настройка Django окружения
sys.path.append(r"C:\Dev\module_app")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'module_app.settings')
django.setup()

from pipelines.models import Tube, Pipe


HEADER_KEYWORDS = ["Номер трубы", "Толщина", "Тип трубы"]


def is_header(row):
    """Проверяем, является ли строка заголовком таблицы."""
    row_str = " ".join([str(x) for x in row if x is not None])
    return any(word in row_str for word in HEADER_KEYWORDS)


def extract_number_and_suffix(tube_num: str) -> tuple[int | None, str]:
    """
    Извлекаем число и буквенный суффикс из номера трубы.
    '2941а' -> (2941, 'а'), '195б' -> (195, 'б')
    """
    if not tube_num:
        return None, ""
    m = re.match(r"(\d+)(.*)", str(tube_num).strip())
    if not m:
        return None, ""
    num = int(m.group(1))
    suffix = m.group(2).strip().lower()
    return num, suffix


def parse_range(range_str: str) -> tuple[int, int]:
    """Парсим строку диапазона вида '2941а - 5195' → (2941, 5195)."""
    parts = [p.strip() for p in range_str.split("-")]
    if len(parts) != 2:
        raise ValueError(f"Неверный формат диапазона: {range_str}")
    start, _ = extract_number_and_suffix(parts[0])
    end, _ = extract_number_and_suffix(parts[1])
    return start, end


def find_pipe_for_tube(tube_num: str, pipe_ranges: dict) -> Pipe | None:
    """
    Определяем Pipe для трубы по её номеру и диапазонам.
    Теперь диапазон открыт: (start, end), крайние значения не включаются.
    """
    num, suffix = extract_number_and_suffix(tube_num)
    if num is None:
        return None

    for pipe_id, range_str in pipe_ranges.items():
        start, end = parse_range(range_str)

        # включаем только внутренние значения диапазона
        if start < num < end:
            try:
                return Pipe.objects.get(id=pipe_id)
            except Pipe.DoesNotExist:
                print(f"⚠️ Pipe с id={pipe_id} не найден в БД")
                return None

    return None


def import_tubes(filepath, pipe_ranges: dict):
    print(filepath)
    wb = load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active

    tubes_to_create = []
    header_found = False

    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if is_header(row):
            header_found = True
            continue

        if not header_found:
            continue  # пропускаем строки до таблицы

        if not row[1]:  # пустая строка
            continue
        if is_header(row):  # повторная шапка
            continue

        tube_num = str(row[1]).strip()
        pipe = find_pipe_for_tube(tube_num, pipe_ranges)
        if pipe is None:
            continue  # труба вне диапазонов

        try:
            tube = Tube(
                pipe=pipe,
                tube_num=tube_num,
                tube_length=float(row[2]) if row[2] is not None else 0,
                thickness=float(row[3]) if row[3] is not None else 0,
                tube_type=str(row[4]).strip() if row[4] else 'without',
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
            tubes_to_create.append(tube)
        except Exception as e:
            print(f"⚠️ Ошибка в строке {i}: {e}")
            continue

    if tubes_to_create:
        Tube.objects.bulk_create(tubes_to_create, ignore_conflicts=True)
        print(f"✅ Импортировано труб: {len(tubes_to_create)}")
    else:
        print("⚠️ Данные для импорта не найдены")


if __name__ == "__main__":
    # Пример словаря диапазонов: {pipe_id: "start - end"}
    pipe_ranges = {
        14: "2941а - 5195",
        15: "5195 - 7480",
        16: "7480 - 7600",
    }

    # if len(sys.argv) < 2:
    #     print("Использование: python import_tubes.py file.xlsx")
    #     sys.exit(1)

    # filepath = sys.argv[1]
    filepath = r"C:\Dev\module_app\fixtures\data\nord_uc_2.xlsx"
    import_tubes(filepath, pipe_ranges)
