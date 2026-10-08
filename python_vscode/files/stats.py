"""Компонент логики приложения.

Содержит чистые функции для работы с набором данных: фильтрацию по региону,
извлечение числовых значений и расчёт статистических метрик.

Модуль полностью независим от способа ввода-вывода: он не читает файлы,
не печатает в консоль и не запрашивает данные у пользователя. На вход
принимает уже разобранные данные, на выход отдаёт числа и структуры данных.
Об ошибках сообщает через исключение ValueError с текстом на русском языке.
"""

import difflib
import math

# Строки, которые в исходных данных означают отсутствующее значение.
_MISSING_MARKERS = frozenset(
    ('', 'na', 'n/a', 'nan', 'none', 'null', '-', '--'))

# Шаг таблицы перцентилей по умолчанию (в процентах).
DEFAULT_PERCENTILE_STEP = 5


def parse_number(raw_value):
    """Преобразует текстовое значение ячейки в число.

    Поддерживает запятую в роли десятичного разделителя и распознаёт
    общепринятые обозначения пропущенных значений.

    Args:
        raw_value: Исходное значение ячейки (строка или None).

    Returns:
        Значение типа float либо None, если значение отсутствует.

    Raises:
        ValueError: Если значение непустое, но не является числом.
    """
    if raw_value is None:
        return None

    text = str(raw_value).strip()
    if text.lower() in _MISSING_MARKERS:
        return None

    normalized = text.replace(',', '.').replace(' ', '')
    try:
        number = float(normalized)
    except ValueError:
        raise ValueError(
            'значение "{0}" не является числом'.format(text)) from None

    if math.isnan(number) or math.isinf(number):
        raise ValueError(
            'значение "{0}" не является конечным числом'.format(text))
    return number


def is_numeric_column(rows, column):
    """Проверяет, можно ли считать колонку числовой.

    Колонка считается числовой, если в ней есть хотя бы одно заполненное
    значение и все заполненные значения разбираются как числа.

    Args:
        rows: Список строк набора данных (словари "колонка -> значение").
        column: Имя проверяемой колонки.

    Returns:
        True, если колонка числовая, иначе False.
    """
    has_value = False
    for row in rows:
        try:
            number = parse_number(row.get(column))
        except ValueError:
            return False
        if number is not None:
            has_value = True
    return has_value


def get_numeric_columns(rows, columns):
    """Возвращает список числовых колонок с сохранением исходного порядка.

    Args:
        rows: Список строк набора данных.
        columns: Список имён всех колонок.

    Returns:
        Список имён колонок, пригодных для расчёта метрик.
    """
    return [column for column in columns if is_numeric_column(rows, column)]


def get_regions(rows, region_column):
    """Возвращает отсортированный список уникальных регионов.

    Args:
        rows: Список строк набора данных.
        region_column: Имя колонки с названием региона.

    Returns:
        Отсортированный список непустых названий регионов.

    Raises:
        ValueError: Если в наборе данных нет колонки с регионами.
    """
    if not rows:
        return []
    if region_column not in rows[0]:
        raise ValueError(
            'в файле отсутствует колонка "{0}"'.format(region_column))

    names = set()
    for row in rows:
        value = (row.get(region_column) or '').strip()
        if value:
            names.add(value)
    return sorted(names)


def find_region(regions, user_input):
    """Ищет точное название региона без учёта регистра и лишних пробелов.

    Args:
        regions: Список известных названий регионов.
        user_input: Текст, введённый пользователем.

    Returns:
        Каноническое название региона из набора данных.

    Raises:
        ValueError: Если название пустое или регион не найден.
    """
    query = (user_input or '').strip()
    if not query:
        raise ValueError('название региона не может быть пустым')

    lowered = query.lower()
    for region in regions:
        if region.lower() == lowered:
            return region
    raise ValueError('регион "{0}" не найден в файле'.format(query))


def suggest_regions(regions, user_input, limit=5):
    """Подбирает похожие названия регионов для подсказки пользователю.

    Args:
        regions: Список известных названий регионов.
        user_input: Текст, введённый пользователем.
        limit: Максимальное количество подсказок.

    Returns:
        Список похожих названий (возможно, пустой).
    """
    query = (user_input or '').strip().lower()
    if not query:
        return []

    matches = [region for region in regions if query in region.lower()]
    if matches:
        return matches[:limit]

    # Совпадений по подстроке нет — ищем близкие по написанию варианты.
    # Сравниваем в нижнем регистре, но возвращаем исходные названия.
    by_lower = {region.lower(): region for region in regions}
    close = difflib.get_close_matches(query, list(by_lower), n=limit,
                                      cutoff=0.5)
    return [by_lower[name] for name in close]


def filter_by_region(rows, region_column, region):
    """Отбирает строки, относящиеся к указанному региону.

    Args:
        rows: Список строк набора данных.
        region_column: Имя колонки с названием региона.
        region: Каноническое название региона.

    Returns:
        Список строк выбранного региона.

    Raises:
        ValueError: Если для региона не найдено ни одной строки.
    """
    selected = [row for row in rows
                if (row.get(region_column) or '').strip() == region]
    if not selected:
        raise ValueError(
            'для региона "{0}" нет ни одной записи'.format(region))
    return selected


def extract_values(rows, column):
    """Извлекает числовые значения колонки, пропуская пустые ячейки.

    Args:
        rows: Список строк набора данных.
        column: Имя колонки.

    Returns:
        Кортеж (values, skipped), где values — список чисел,
        skipped — количество пропущенных (пустых) ячеек.

    Raises:
        ValueError: Если колонки нет, значение не является числом
            или не осталось ни одного значения для расчёта.
    """
    if rows and column not in rows[0]:
        raise ValueError('колонка "{0}" отсутствует в данных'.format(column))

    values = []
    skipped = 0
    for number, row in enumerate(rows, start=1):
        try:
            parsed = parse_number(row.get(column))
        except ValueError as error:
            raise ValueError(
                'колонка "{0}", запись {1}: {2}'.format(column, number, error))
        if parsed is None:
            skipped += 1
        else:
            values.append(parsed)

    if not values:
        raise ValueError(
            'в колонке "{0}" нет ни одного заполненного значения '
            'для выбранного региона'.format(column))
    return values, skipped


def calculate_mean(values):
    """Вычисляет среднее арифметическое.

    Args:
        values: Непустой список чисел.

    Returns:
        Среднее значение.

    Raises:
        ValueError: Если список пуст.
    """
    if not values:
        raise ValueError('невозможно вычислить среднее: нет данных')
    return sum(values) / len(values)


def calculate_median(values):
    """Вычисляет медиану.

    При чётном количестве элементов возвращает среднее двух центральных.

    Args:
        values: Непустой список чисел.

    Returns:
        Медиана выборки.

    Raises:
        ValueError: Если список пуст.
    """
    if not values:
        raise ValueError('невозможно вычислить медиану: нет данных')

    ordered = sorted(values)
    count = len(ordered)
    middle = count // 2
    if count % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def calculate_percentile(values, percent):
    """Вычисляет перцентиль методом ближайшего ранга.

    N-й перцентиль — такое число X из выборки, что не менее N% элементов
    меньше либо равны X.

    Args:
        values: Непустой список чисел.
        percent: Порядок перцентиля в диапазоне от 0 до 100.

    Returns:
        Значение перцентиля.

    Raises:
        ValueError: Если список пуст или порядок вне диапазона [0, 100].
    """
    if not values:
        raise ValueError('невозможно вычислить перцентиль: нет данных')
    if not 0 <= percent <= 100:
        raise ValueError(
            'перцентиль должен быть в диапазоне от 0 до 100, получено {0}'
            .format(percent))

    ordered = sorted(values)
    rank = math.ceil(percent / 100 * len(ordered))
    index = max(rank, 1) - 1
    return ordered[index]


def calculate_metrics(values):
    """Считает основные статистические метрики выборки.

    Args:
        values: Непустой список чисел.

    Returns:
        Словарь с ключами count, min, max, median, mean.

    Raises:
        ValueError: Если список пуст.
    """
    if not values:
        raise ValueError('невозможно вычислить метрики: нет данных')

    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'median': calculate_median(values),
        'mean': calculate_mean(values),
    }


def calculate_percentile_table(values, step=DEFAULT_PERCENTILE_STEP):
    """Строит таблицу перцентилей от 0 до 100 с заданным шагом.

    Args:
        values: Непустой список чисел.
        step: Шаг в процентах (целое число больше нуля).

    Returns:
        Список кортежей (процент, значение перцентиля).

    Raises:
        ValueError: Если список пуст или шаг некорректен.
    """
    if not isinstance(step, int) or step <= 0 or step > 100:
        raise ValueError(
            'шаг перцентилей должен быть целым числом от 1 до 100')

    percents = list(range(0, 101, step))
    if percents[-1] != 100:
        percents.append(100)
    return [(percent, calculate_percentile(values, percent))
            for percent in percents]
