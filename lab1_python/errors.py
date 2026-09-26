class AppError(Exception):
    """Базовая ошибка приложения."""


class DatasetFileError(AppError):
    """Проблемы с файлом: не найден, пустой, слишком большой, не читается."""


class DatasetContentError(AppError):
    """Файл открыт, но данные некорректны: нет нужных колонок, битые строки."""


class RegionNotFoundError(AppError):
    """Введённого региона нет в данных."""


class ColumnNotFoundError(AppError):
    """Введённой колонки нет или она нечисловая."""


class EmptyResultError(AppError):
    """После фильтрации по региону не осталось данных."""
