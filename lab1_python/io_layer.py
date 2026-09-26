"""Слой ввода-вывода: проверка файла, чтение CSV, форматированный вывод.

Не содержит логики расчётов: только чтение, парсинг и печать.
"""

import csv
import os

from errors import DatasetContentError, DatasetFileError

BYTES_IN_KB = 1024
BYTES_IN_MB = BYTES_IN_KB * BYTES_IN_KB
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * BYTES_IN_MB

CSV_EXTENSION = ".csv"
# utf-8-sig отбрасывает BOM, если он есть, и работает как utf-8, если его нет.
CSV_ENCODING = "utf-8-sig"
REGION_COLUMN = "region"

EMPTY_CELL = ""
COLUMN_SEPARATOR = " | "


def validate_file(path):
    """Проверки до открытия файла."""
    if not path:
        raise DatasetFileError("Путь до файла не может быть пустым.")
    if not os.path.exists(path):
        raise DatasetFileError(f"Файл '{path}' не найден.")
    if not os.path.isfile(path):
        raise DatasetFileError(f"'{path}' — это не файл.")
    if not path.lower().endswith(CSV_EXTENSION):
        raise DatasetFileError(f"Ожидается файл с расширением {CSV_EXTENSION}.")

    size = os.path.getsize(path)
    if size == 0:
        raise DatasetFileError("Файл пустой — в нём нет данных.")
    if size > MAX_FILE_SIZE_BYTES:
        raise DatasetFileError(
            f"Файл слишком большой ({size // BYTES_IN_MB} МБ). "
            f"Максимум — {MAX_FILE_SIZE_MB} МБ."
        )


def read_dataset(path):
    """Прочитать CSV и вернуть (строки, колонки).

    Все ошибки файла и содержимого приводятся к AppError-наследникам,
    чтобы вызывающий код не разбирался с OSError и UnicodeDecodeError.
    """
    validate_file(path)

    try:
        with open(path, encoding=CSV_ENCODING, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            columns = reader.fieldnames
    except UnicodeDecodeError:
        raise DatasetFileError("Файл не читается: ожидается кодировка UTF-8.") from None
    except OSError as error:
        raise DatasetFileError(f"Не удалось прочитать файл: {error}") from None

    if not columns or REGION_COLUMN not in columns:
        raise DatasetContentError(
            f"В файле нет обязательной колонки '{REGION_COLUMN}'."
        )
    if not rows:
        raise DatasetContentError("Файл не содержит строк с данными.")

    return rows, columns


def cell_text(row, column):
    """Значение ячейки как строка.

    DictReader подставляет None, если в строке меньше полей, чем в заголовке,
    и список лишних значений, если полей больше. И то, и другое приводим
    к строке, иначе форматирование таблицы падает.
    """
    value = row.get(column)
    if value is None:
        return EMPTY_CELL
    if isinstance(value, list):
        return COLUMN_SEPARATOR.join(str(item) for item in value)
    return str(value)


def print_rows_table(rows, columns):
    if not rows:
        print("Нет строк для отображения.")
        return

    widths = {}
    for column in columns:
        lengths = [len(cell_text(row, column)) for row in rows]
        widths[column] = max(len(column), max(lengths))

    header = [f"{column:<{widths[column]}}" for column in columns]
    print(COLUMN_SEPARATOR.join(header))
    for row in rows:
        line = [f"{cell_text(row, column):<{widths[column]}}" for column in columns]
        print(COLUMN_SEPARATOR.join(line))
