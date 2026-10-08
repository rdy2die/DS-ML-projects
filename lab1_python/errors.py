"""Иерархия ошибок приложения.

Каждая конкретная причина — отдельный класс, чтобы её можно было
и опознать в коде (except по нужному типу), и показать пользователю
своим текстом. Базовые классы нужны, чтобы ловить группами:
except DatasetFileError — любая проблема с файлом,
except AppError — любая ожидаемая ошибка приложения.
"""


class AppError(Exception):
    """Базовая ошибка приложения."""


# --------------------------------------------------------------------------
# Ошибки файла: возникают до того, как удалось прочитать содержимое.
# --------------------------------------------------------------------------


class DatasetFileError(AppError):
    """Базовая ошибка файла."""


class EmptyPathError(DatasetFileError):
    """Пользователь не ввёл путь."""


class DatasetNotFoundError(DatasetFileError):
    """По указанному пути ничего нет."""


class NotAFileError(DatasetFileError):
    """Путь есть, но это папка или устройство, а не файл."""


class WrongExtensionError(DatasetFileError):
    """Расширение не .csv."""


class EmptyFileError(DatasetFileError):
    """Файл существует, но его размер 0 байт."""


class FileTooLargeError(DatasetFileError):
    """Файл больше допустимого размера."""


class FileEncodingError(DatasetFileError):
    """Файл не в UTF-8."""


class FileReadError(DatasetFileError):
    """Файл не читается по причине уровня ОС: нет прав, занят, сбой диска."""


# --------------------------------------------------------------------------
# Ошибки содержимого: файл прочитан, но данные не те.
# --------------------------------------------------------------------------


class DatasetContentError(AppError):
    """Базовая ошибка содержимого."""


class MissingColumnError(DatasetContentError):
    """В заголовке CSV нет обязательной колонки."""


class NoDataRowsError(DatasetContentError):
    """Есть заголовок, но ни одной строки с данными."""


class NoRegionsError(DatasetContentError):
    """Колонка region есть, но все её значения пустые."""


class NoMetricColumnsError(DatasetContentError):
    """Кроме region в файле нет ни одной колонки."""


# --------------------------------------------------------------------------
# Ошибки выбора пользователя.
# --------------------------------------------------------------------------


class ChoiceError(AppError):
    """Базовая ошибка выбора пункта меню."""


class MenuIndexError(ChoiceError):
    """Введён номер вне диапазона списка."""


class RegionNotFoundError(ChoiceError):
    """Введённого региона нет в данных."""


class ColumnNotFoundError(ChoiceError):
    """Введённой колонки нет в данных."""


# --------------------------------------------------------------------------
# Ошибки результата.
# --------------------------------------------------------------------------


class EmptyResultError(AppError):
    """После фильтрации не осталось числовых данных."""
