"""Компонент ввода-вывода: форматированный вывод в консоль.

Модуль умеет только печатать готовые данные. Он ничего не вычисляет и не
читает — все значения приходят из компонента логики.
"""

# Текст, которым обозначается отсутствующее значение в таблице.
MISSING_TEXT = 'н/д'

# Количество знаков после запятой при выводе метрик.
_PRECISION = 3


def format_number(value):
    """Приводит число к компактному виду для вывода.

    Args:
        value: Число или None.

    Returns:
        Строковое представление числа; для None — обозначение пропуска.
    """
    if value is None:
        return MISSING_TEXT
    if isinstance(value, int):
        return str(value)

    text = '{0:.{1}f}'.format(value, _PRECISION)
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text or '0'


def format_table(headers, rows):
    """Собирает текстовую таблицу с рамкой из псевдографики.

    Ширина каждой колонки подбирается по самому длинному значению.

    Args:
        headers: Список заголовков колонок.
        rows: Список строк, каждая — список значений (любого типа).

    Returns:
        Готовая к печати многострочная строка.
    """
    headers = [str(header) for header in headers]
    text_rows = [[MISSING_TEXT if cell is None or cell == '' else str(cell)
                  for cell in row] for row in rows]

    widths = [len(header) for header in headers]
    for row in text_rows:
        for index, cell in enumerate(row):
            if index < len(widths):
                widths[index] = max(widths[index], len(cell))

    def build_line(left, middle, right):
        """Строит горизонтальную линию рамки."""
        return left + middle.join('─' * (width + 2) for width in widths) + right

    def build_row(cells):
        """Строит строку таблицы с выравниванием по ширине колонок."""
        parts = []
        for index, width in enumerate(widths):
            cell = cells[index] if index < len(cells) else ''
            parts.append(' {0} '.format(cell.ljust(width)))
        return '│' + '│'.join(parts) + '│'

    lines = [build_line('┌', '┬', '┐'), build_row(headers),
             build_line('├', '┼', '┤')]
    lines.extend(build_row(row) for row in text_rows)
    lines.append(build_line('└', '┴', '┘'))
    return '\n'.join(lines)


def print_title(text):
    """Печатает заголовок раздела.

    Args:
        text: Текст заголовка.
    """
    print('\n' + text)
    print('─' * len(text))


def print_error(message):
    """Печатает сообщение об ошибке.

    Args:
        message: Текст ошибки.
    """
    print('\n[ОШИБКА] {0}'.format(message))


def print_info(message):
    """Печатает информационное сообщение.

    Args:
        message: Текст сообщения.
    """
    print('[i] {0}'.format(message))


def print_columns(columns, numeric_columns):
    """Печатает список колонок с их идентификаторами.

    Args:
        columns: Список всех колонок файла.
        numeric_columns: Список колонок, пригодных для расчёта метрик.
    """
    print_title('Колонки файла')
    rows = []
    for column_id, name in enumerate(columns, start=1):
        kind = 'числовая' if name in numeric_columns else 'текстовая'
        rows.append([column_id, name, kind])
    print(format_table(['ID', 'Колонка', 'Тип'], rows))


def print_regions(regions):
    """Печатает список доступных регионов в несколько колонок.

    Args:
        regions: Отсортированный список названий регионов.
    """
    print_title('Доступные регионы ({0})'.format(len(regions)))
    if not regions:
        print('Список пуст.')
        return

    width = max(len(region) for region in regions) + 2
    per_line = max(1, 100 // width)
    for start in range(0, len(regions), per_line):
        chunk = regions[start:start + per_line]
        print(''.join(region.ljust(width) for region in chunk).rstrip())


def print_region_table(columns, rows, region):
    """Печатает все строки набора данных по выбранному региону.

    Args:
        columns: Список имён колонок.
        rows: Отфильтрованные строки региона.
        region: Название региона.
    """
    print_title('Данные по региону: {0} (записей: {1})'
                .format(region, len(rows)))
    table_rows = [[row.get(column, '') for column in columns] for row in rows]
    print(format_table(columns, table_rows))


def print_metrics(column, metrics, skipped):
    """Печатает статистические метрики в текстовых полях.

    Args:
        column: Имя колонки, по которой считались метрики.
        metrics: Словарь метрик из компонента логики.
        skipped: Количество пропущенных пустых значений.
    """
    print_title('Статистические метрики по колонке "{0}"'.format(column))
    fields = (
        ('Учтено значений', metrics['count']),
        ('Пропущено (пустых)', skipped),
        ('Максимум', metrics['max']),
        ('Минимум', metrics['min']),
        ('Медиана', metrics['median']),
        ('Среднее значение', metrics['mean']),
    )
    label_width = max(len(label) for label, _ in fields)
    for label, value in fields:
        print('{0} : {1}'.format(label.ljust(label_width),
                                 format_number(value)))


def print_percentiles(column, percentiles):
    """Печатает таблицу перцентилей.

    Args:
        column: Имя колонки.
        percentiles: Список кортежей (процент, значение).
    """
    print_title('Перцентили по колонке "{0}"'.format(column))
    rows = [['{0}%'.format(percent), format_number(value)]
            for percent, value in percentiles]
    print(format_table(['Перцентиль', 'Значение'], rows))
