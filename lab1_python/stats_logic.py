"""Слой логики: расчёт статистических метрик.

Не содержит ввода-вывода: не печатает, не читает файлы, не спрашивает
пользователя. Работает только со списками чисел и списками строк-словарей.
"""

import math

from errors import EmptyResultError

PERCENT_MIN = 0
PERCENT_MAX = 100
PERCENTILE_STEP = 5
MEDIAN_HALVES = 2


def get_max(data):
    return max(data)


def get_min(data):
    return min(data)


def get_average(data):
    return sum(data) / len(data)


def get_median(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % MEDIAN_HALVES == 0:
        left = sorted_data[n // MEDIAN_HALVES - 1]
        right = sorted_data[n // MEDIAN_HALVES]
        median = (left + right) / MEDIAN_HALVES
    else:
        median = sorted_data[n // MEDIAN_HALVES]
    return median


def percentile(data, percent):
    """N-й перцентиль: наименьшее X, для которого N% элементов <= X.

    Метод nearest-rank: индекс = ceil(len * percent / 100) - 1.
    """
    sorted_data = sorted(data)
    index = math.ceil(len(sorted_data) * percent / PERCENT_MAX) - 1
    return sorted_data[max(index, 0)]


def create_table(data):
    """Таблица перцентилей от 0 до 100 с шагом 5."""
    per_list = []
    for percent in range(PERCENT_MIN, PERCENT_MAX + 1, PERCENTILE_STEP):
        per_list.append((percent, percentile(data, percent)))
    return per_list


def filter_by_region(rows, region_column, region):
    """Оставить только строки выбранного региона."""
    return [row for row in rows if row[region_column] == region]


def collect_regions(rows, region_column):
    """Отсортированный список уникальных непустых регионов."""
    regions = {row[region_column] for row in rows if row[region_column]}
    return sorted(regions)


def extract_values(rows, column):
    """Превратить колонку в список float.

    Возвращает (значения, число пропущенных). Пропускает нечисловые
    и пустые ячейки. Если числовых значений нет вообще — EmptyResultError.
    """
    values = []
    skipped = 0
    for row in rows:
        try:
            values.append(float(row[column]))
        except (ValueError, TypeError):
            skipped += 1
    if not values:
        raise EmptyResultError(f"В колонке '{column}' нет числовых данных.")
    return values, skipped
