class AppError(Exception):
    """Базовая ошибка приложения."""


class DatasetFileError(AppError):
    """Проблемы с файлом: не найден, пустой, слишком большой, не читается."""


class DatasetContentError(AppError):
    """Файл открыт, но данные некорректны: нет нужных колонок, битые строки."""


class EmptyResultError(AppError):
    """После фильтрации не осталось числовых данных."""
