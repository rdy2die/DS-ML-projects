import os

from errors import DatasetFileError

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 МБ


def validate_file(path):
    if not path:
        raise DatasetFileError("Путь до файла не может быть пустым.")
    if not os.path.exists(path):
        raise DatasetFileError(f"Файл '{path}' не найден.")
    if not os.path.isfile(path):
        raise DatasetFileError(f"'{path}' — это не файл.")
    if not path.lower().endswith(".csv"):
        raise DatasetFileError("Ожидается файл с расширением .csv.")

    size = os.path.getsize(path)
    if size == 0:
        raise DatasetFileError("Файл пустой — в нём нет данных.")
    if size > MAX_FILE_SIZE_BYTES:
        raise DatasetFileError(
            f"Файл слишком большой ({size // 1024 // 1024} МБ). Максимум — 50 МБ."
        )


def print_rows_table(rows, columns):
    if not rows:
        print("Нет строк для отображения.")
        return
    widths = {}
    for col in columns:
        lengths = [len(row[col]) for row in rows]
        widths[col] = max(len(col), max(lengths))
    header = [f"{col:<{widths[col]}}" for col in columns]
    print(" | ".join(header))
    for row in rows:
        line = [f"{row[col]:<{widths[col]}}" for col in columns]
        print(" | ".join(line))