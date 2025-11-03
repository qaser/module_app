import sys
import os
import re
import django
from openpyxl import load_workbook
from datetime import datetime, date

# Настройка Django окружения
sys.path.append(r"H:\WorkDocuments\Dev\module_app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "module_app.settings")
django.setup()

from pipelines.models import Pipe, Tube, TubeVersion, Diagnostics

Tube.objects.all().delete()
TubeVersion.objects.all().delete()
Diagnostics.objects.all().delete()


HEADER_KEYWORDS = ["Номер трубы", "Толщина", "Тип трубы"]


from pipelines.models import Pipe, Tube, TubeVersion, Diagnostics


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


if __name__ == "__main__":
    pipe_ranges = {
        14: "2941а - 5195",
        15: "5195 - 7480",
        16: "7480 - 7600",
    }
    diagnostics_start = '04.04.2025'
    diagnostics_end = '07.04.2025'
    filepath = r"H:\WorkDocuments\Dev\module_app\fixtures\data\nord_uc_2.xlsx"
    import_tubes(filepath, pipe_ranges, diagnostics_start, diagnostics_end)
