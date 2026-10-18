"""Слой ввода: чтение таблиц из файлов.

Модуль ничего не считает и ничего не рисует. Его задача - прочитать файл,
превратить его в таблицу и сразу сказать понятным языком, если файла нет,
он пустой, битый или в нем не хватает нужных столбцов.
"""

from pathlib import Path

import pandas as pd

from errors import (
    ColumnTypeError,
    DataFileAccessError,
    DataFileNotFoundError,
    DataFormatError,
    EmptyDataFileError,
    EncodingError,
)
from validation import require_columns

# utf-8-sig понимает обычный UTF-8 и дополнительно убирает BOM - невидимый
# символ в начале файла, из-за которого первый столбец "теряется".
DEFAULT_ENCODING = "utf-8-sig"


def load_csv(
    path,
    required_columns=(),
    numeric_columns=(),
    encoding=DEFAULT_ENCODING,
    sep=",",
    header="infer",
    names=None,
):
    """Прочитать таблицу из текстового файла и проверить ее пригодность.

    required_columns - столбцы, без которых работать нельзя.
    numeric_columns - столбцы, которые обязаны быть числовыми. Значения,
    которые не удалось распознать как число, становятся пустыми (NaN).
    sep, header, names - как в pandas.read_csv: разделитель, строка
    заголовка и имена столбцов для файлов без заголовка.

    Возвращает DataFrame. При любой проблеме поднимает наследника LabError.
    """
    file_path = Path(path)
    data = _read_file(file_path, encoding, sep, header, names)

    if data.empty:
        raise EmptyDataFileError(file_path)

    source = f"файле {file_path.name}"
    require_columns(data, required_columns, source)

    for column in numeric_columns:
        data[column] = _to_numeric(data, column, file_path.name)

    return data


def _read_file(file_path, encoding, sep, header, names):
    """Прочитать файл, переведя ошибки pandas в ошибки проекта."""
    try:
        return pd.read_csv(
            file_path,
            encoding=encoding,
            sep=sep,
            header=header,
            names=names,
        )
    except FileNotFoundError:
        raise DataFileNotFoundError(file_path) from None
    except pd.errors.EmptyDataError:
        raise EmptyDataFileError(file_path) from None
    except pd.errors.ParserError as error:
        raise DataFormatError(file_path, error) from None
    except UnicodeDecodeError:
        raise EncodingError(file_path, encoding) from None
    except OSError as error:
        # Сюда попадают папка вместо файла, нет прав на чтение и прочее.
        raise DataFileAccessError(file_path, error) from None


def _to_numeric(data, column, source):
    """Привести столбец к числам; пустые значения оставить пустыми."""
    converted = pd.to_numeric(data[column], errors="coerce")
    if converted.notna().sum() == 0:
        raise ColumnTypeError(column, source)
    return converted
