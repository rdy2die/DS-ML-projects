"""Слой ввода-вывода: проверка файла, чтение CSV, форматированный вывод.

Не содержит логики расчётов: только чтение, парсинг и печать.
"""

import csv
import os

from errors import (
    DatasetNotFoundError,
    EmptyFileError,
    EmptyPathError,
    FileEncodingError,
    FileReadError,
    FileTooLargeError,
    MissingColumnError,
    NoDataRowsError,
    NotAFileError,
    WrongExtensionError,
)

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
    """Проверки до открытия файла. Каждая причина — своё исключение."""
    if not path:
        raise EmptyPathError("путь до файла не может быть пустым.")

    if not os.path.exists(path):
        raise DatasetNotFoundError(f"файл '{path}' не найден.")

    if not os.path.isfile(path):
        raise NotAFileError(f"'{path}' — это не файл, а папка или устройство.")

    if not path.lower().endswith(CSV_EXTENSION):
        raise WrongExtensionError(
            f"ожидается файл с расширением {CSV_EXTENSION}, "
            f"а у '{os.path.basename(path)}' другое."
        )

    size = os.path.getsize(path)
    if size == 0:
        raise EmptyFileError(f"файл '{os.path.basename(path)}' пустой (0 байт).")
    if size > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            f"файл слишком большой ({size // BYTES_IN_MB} МБ). "
            f"Максимум — {MAX_FILE_SIZE_MB} МБ."
        )


def read_dataset(path):
    """Прочитать CSV и вернуть (строки, колонки).

    Системные исключения приводятся к доменным, чтобы вызывающий код
    не разбирался с OSError и UnicodeDecodeError напрямую.
    """
    validate_file(path)

    try:
        with open(path, encoding=CSV_ENCODING, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            columns = reader.fieldnames
    except UnicodeDecodeError as error:
        raise FileEncodingError(
            f"файл не в кодировке UTF-8 — не удалось прочитать байт "
            f"в позиции {error.start}. Пересохраните файл в UTF-8."
        ) from None
    except PermissionError:
        raise FileReadError(f"нет прав на чтение файла '{path}'.") from None
    except OSError as error:
        raise FileReadError(
            f"не удалось прочитать файл: {error.strerror or error}."
        ) from None

    if not columns:
        raise MissingColumnError("в файле нет строки заголовка с названиями колонок.")
    if REGION_COLUMN not in columns:
        raise MissingColumnError(
            f"в файле нет обязательной колонки '{REGION_COLUMN}'. "
            f"Найдены колонки: {', '.join(columns)}."
        )
    if not rows:
        raise NoDataRowsError(
            "в файле есть только заголовок, ни одной строки с данными."
        )

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
