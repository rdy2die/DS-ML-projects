"""Классы ошибок проекта.

Все ошибки наследуются от LabError. Благодаря этому вызывающий код ловит
их одним except и показывает пользователю готовое сообщение на русском
языке, без технического трейсбека.
"""


def _one_line(reason):
    """Превратить текст ошибки библиотеки в одну строку без переносов."""
    return " ".join(str(reason).split())


class LabError(Exception):
    """Базовая ошибка проекта.

    Текст ошибки рассчитан на пользователя: он говорит, что именно пошло
    не так и что с этим делать.
    """


class DataFileNotFoundError(LabError):
    """Файла с данными нет по указанному пути."""

    def __init__(self, path):
        self.path = path
        super().__init__(
            f"Файл с данными не найден: {path}. "
            "Проверьте название файла и положите его в ту же папку, "
            "где лежит ноутбук."
        )


class DataFileAccessError(LabError):
    """Файл существует, но открыть его не удалось."""

    def __init__(self, path, reason):
        self.path = path
        self.reason = _one_line(reason)
        super().__init__(
            f"Не удалось открыть файл {path}: {self.reason}. "
            "Проверьте, что это файл, а не папка, и что он доступен "
            "для чтения."
        )


class EmptyDataFileError(LabError):
    """В файле нет ни одной строки с данными."""

    def __init__(self, path):
        self.path = path
        super().__init__(
            f"Файл {path} пустой: в нем нет строк с данными. "
            "Скачайте файл заново."
        )


class DataFormatError(LabError):
    """Файл не разбирается как таблица CSV."""

    def __init__(self, path, reason):
        self.path = path
        self.reason = _one_line(reason)
        super().__init__(
            f"Файл {path} не читается как таблица CSV: {self.reason}. "
            "Проверьте разделители и то, что во всех строках одинаковое "
            "число столбцов."
        )


class EncodingError(LabError):
    """Файл сохранен в другой кодировке."""

    def __init__(self, path, encoding):
        self.path = path
        self.encoding = encoding
        super().__init__(
            f"Файл {path} не читается в кодировке {encoding}. "
            "Пересохраните его в UTF-8 или передайте нужную кодировку "
            "параметром encoding."
        )


class MissingColumnsError(LabError):
    """В таблице нет столбцов, без которых расчет невозможен."""

    def __init__(self, missing, available, source="таблице"):
        self.missing = list(missing)
        self.available = list(available)
        super().__init__(
            f"В {source} нет нужных столбцов: "
            f"{', '.join(map(str, self.missing))}. "
            f"Доступные столбцы: {', '.join(map(str, self.available))}."
        )


class ColumnTypeError(LabError):
    """Столбец должен быть числовым, но чисел в нем нет."""

    def __init__(self, column, source=None):
        self.column = column
        where = f" в файле {source}" if source else ""
        super().__init__(
            f"Столбец {column}{where} должен содержать числа, но ни одно "
            "значение в нем не распознано как число. Проверьте, тот ли это "
            "столбец и каким знаком отделяется дробная часть."
        )


class NoDataError(LabError):
    """После проверок и фильтров не осталось данных для расчета."""

    def __init__(self, what):
        self.what = what
        super().__init__(
            f"Нет данных для расчета: {what}. "
            "Либо таблица не загрузилась, либо все строки отсеялись "
            "как пустые или некорректные."
        )


class InvalidParameterError(LabError):
    """Пользователь задал некорректное значение параметра."""

    def __init__(self, name, value, requirement):
        self.name = name
        self.value = value
        super().__init__(
            f"Некорректное значение параметра {name}: {value!r}. "
            f"Ожидается {requirement}."
        )
