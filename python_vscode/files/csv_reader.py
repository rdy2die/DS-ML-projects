"""Компонент ввода-вывода: чтение CSV-файла.

Модуль отвечает только за чтение файла с диска и его разбор в структуру
данных Python. Никакой обработки и анализа данных здесь нет.

Все ожидаемые проблемы (отсутствие файла, нет прав, битая кодировка,
нарушенная структура) преобразуются в исключение ValueError с понятным
пользователю текстом.
"""

import csv
import os

# Кодировки перебираются по очереди: utf-8-sig дополнительно снимает BOM.
_ENCODINGS = ('utf-8-sig', 'cp1251')

# Разделители, которые пытается распознать csv.Sniffer.
_DELIMITERS = ',;\t|'

# Ограничение на размер файла, чтобы не пытаться читать гигабайтные данные.
_MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024


def _check_path(path):
    """Проверяет, что по пути находится доступный непустой файл.

    Args:
        path: Путь к файлу.

    Raises:
        ValueError: Если путь пуст, файла нет, это папка, нет прав на
            чтение, файл пуст или слишком велик.
    """
    if not path or not path.strip():
        raise ValueError('путь к файлу не указан')

    if not os.path.exists(path):
        raise ValueError('файл "{0}" не найден'.format(path))

    if os.path.isdir(path):
        raise ValueError('"{0}" — это папка, а не файл'.format(path))

    if not os.path.isfile(path):
        raise ValueError('"{0}" не является обычным файлом'.format(path))

    if not os.access(path, os.R_OK):
        raise ValueError('нет прав на чтение файла "{0}"'.format(path))

    try:
        size = os.path.getsize(path)
    except OSError as error:
        raise ValueError(
            'не удалось получить размер файла "{0}": {1}'.format(path, error))

    if size == 0:
        raise ValueError('файл "{0}" пуст'.format(path))

    if size > _MAX_FILE_SIZE_BYTES:
        raise ValueError(
            'файл "{0}" слишком большой ({1:.1f} МБ), ожидается не более '
            '{2} МБ'.format(path, size / 1024 / 1024,
                            _MAX_FILE_SIZE_BYTES // 1024 // 1024))


def _read_text(path):
    """Читает файл целиком, подбирая кодировку.

    Args:
        path: Путь к файлу.

    Returns:
        Содержимое файла в виде строки.

    Raises:
        ValueError: Если файл не читается ни в одной из кодировок или
            произошла ошибка операционной системы.
    """
    last_decode_error = None
    for encoding in _ENCODINGS:
        try:
            with open(path, 'r', encoding=encoding, newline='') as source:
                return source.read()
        except UnicodeDecodeError as error:
            last_decode_error = error
        except PermissionError:
            raise ValueError(
                'нет прав на чтение файла "{0}"'.format(path)) from None
        except IsADirectoryError:
            raise ValueError(
                '"{0}" — это папка, а не файл'.format(path)) from None
        except OSError as error:
            raise ValueError(
                'ошибка чтения файла "{0}": {1}'.format(path, error)) from None

    raise ValueError(
        'не удалось определить кодировку файла "{0}" (проверены: {1}). '
        'Подробности: {2}'.format(path, ', '.join(_ENCODINGS),
                                  last_decode_error))


def _detect_delimiter(text):
    """Определяет разделитель колонок по первой строке файла.

    Args:
        text: Содержимое файла.

    Returns:
        Символ-разделитель. Если распознать не удалось, возвращает запятую.
    """
    sample = text[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=_DELIMITERS).delimiter
    except csv.Error:
        # Sniffer не справился (например, одна колонка) — берём запятую.
        return ','


def _validate_header(header, path):
    """Проверяет корректность строки заголовков.

    Args:
        header: Список имён колонок.
        path: Путь к файлу (для текста ошибки).

    Returns:
        Список имён колонок без лишних пробелов.

    Raises:
        ValueError: Если заголовок пуст, содержит пустые имена или дубликаты.
    """
    if not header:
        raise ValueError(
            'в файле "{0}" отсутствует строка заголовков'.format(path))

    columns = [name.strip() for name in header]

    empty_positions = [str(index) for index, name in enumerate(columns, 1)
                       if not name]
    if empty_positions:
        raise ValueError(
            'в заголовке файла "{0}" пустые имена колонок в позициях: {1}'
            .format(path, ', '.join(empty_positions)))

    duplicates = sorted({name for name in columns if columns.count(name) > 1})
    if duplicates:
        raise ValueError(
            'в заголовке файла "{0}" повторяются колонки: {1}'
            .format(path, ', '.join(duplicates)))

    if len(columns) < 2:
        raise ValueError(
            'в файле "{0}" распознана всего одна колонка — возможно, неверный '
            'разделитель или это не CSV-файл'.format(path))
    return columns


def read_csv(path):
    """Читает CSV-файл и возвращает заголовки и строки данных.

    Args:
        path: Путь к CSV-файлу.

    Returns:
        Кортеж (columns, rows): список имён колонок и список строк,
        где каждая строка — словарь "имя колонки -> значение (строка)".

    Raises:
        ValueError: При любой проблеме с файлом или его структурой.
    """
    _check_path(path)
    text = _read_text(path)
    delimiter = _detect_delimiter(text)

    reader = csv.reader(text.splitlines(), delimiter=delimiter)
    try:
        header = next(reader, None)
    except csv.Error as error:
        raise ValueError(
            'не удалось разобрать заголовок файла "{0}": {1}'
            .format(path, error)) from None

    columns = _validate_header(header, path)

    rows = []
    try:
        for line_number, raw_row in enumerate(reader, start=2):
            if not raw_row or all(not cell.strip() for cell in raw_row):
                continue  # Пустые строки просто пропускаем.

            if len(raw_row) != len(columns):
                raise ValueError(
                    'строка {0} файла "{1}": ожидалось {2} значений, '
                    'найдено {3}'.format(line_number, path, len(columns),
                                         len(raw_row)))
            rows.append(dict(zip(columns, (cell.strip()
                                           for cell in raw_row))))
    except csv.Error as error:
        raise ValueError(
            'ошибка разбора файла "{0}": {1}'.format(path, error)) from None

    if not rows:
        raise ValueError(
            'в файле "{0}" есть заголовок, но нет ни одной строки данных'
            .format(path))
    return columns, rows
