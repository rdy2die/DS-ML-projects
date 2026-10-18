"""Общие проверки входных данных.

Модуль не считает и не рисует: он только убеждается, что данные пригодны
для работы, и поднимает понятную ошибку, если это не так. Проверки вынесены
отдельно, чтобы не дублировать их в слое логики и в слое вывода (DRY).
"""

import pandas as pd

from errors import (
    InvalidParameterError,
    MissingColumnsError,
    NoDataError,
)


def require_table(data, what="таблица"):
    """Убедиться, что на входе непустая таблица."""
    if not isinstance(data, pd.DataFrame):
        raise NoDataError(f"{what} не загружена")
    if data.empty:
        raise NoDataError(f"{what} пустая")


def require_columns(data, columns, source="таблице"):
    """Убедиться, что в таблице есть все перечисленные столбцы."""
    require_table(data)
    missing = [name for name in columns if name not in data.columns]
    if missing:
        raise MissingColumnsError(missing, data.columns, source)


def require_values(values, what):
    """Убедиться, что в наборе значений есть хотя бы одна строка."""
    if values is None or len(values) == 0:
        raise NoDataError(what)


def require_positive(name, value):
    """Убедиться, что параметр строго больше нуля."""
    if not isinstance(value, (int, float)) or value <= 0:
        raise InvalidParameterError(name, value, "число больше нуля")


def require_positive_int(name, value):
    """Убедиться, что параметр - целое число не меньше единицы."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise InvalidParameterError(name, value, "целое число не меньше 1")


def require_non_negative_int(name, value):
    """Убедиться, что параметр - целое число не меньше нуля."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise InvalidParameterError(name, value, "целое число не меньше 0")
