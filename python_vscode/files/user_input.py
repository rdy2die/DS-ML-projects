"""Компонент ввода-вывода: получение данных от пользователя.

Каждая функция запрашивает значение, проверяет его формат и при ошибке
показывает понятное сообщение и просит ввести значение заново. Логика
обработки данных вынесена в модуль stats.
"""

import console_output
import stats

# Команда, по которой пользователю показывается список регионов.
HELP_COMMAND = '?'

# Ответы, которые трактуются как согласие.
_YES_ANSWERS = frozenset(('д', 'да', 'y', 'yes'))
_NO_ANSWERS = frozenset(('н', 'нет', 'n', 'no'))


def ask_text(prompt):
    """Запрашивает строку у пользователя.

    Args:
        prompt: Приглашение ко вводу.

    Returns:
        Введённая строка без крайних пробелов.

    Raises:
        EOFError: Если поток ввода закрыт (например, Ctrl+D).
    """
    return input(prompt).strip()


def ask_file_path(prompt='Укажите путь к CSV-файлу: '):
    """Запрашивает у пользователя путь к файлу.

    Args:
        prompt: Приглашение ко вводу.

    Returns:
        Путь к файлу без крайних пробелов и кавычек.
    """
    while True:
        # Пользователь мог перетащить файл в терминал — снимаем кавычки.
        path = ask_text(prompt).strip('"').strip("'")
        if path:
            return path
        console_output.print_error('путь к файлу не может быть пустым')


def ask_region(regions):
    """Запрашивает название региона, повторяя ввод при ошибке.

    Args:
        regions: Список доступных регионов.

    Returns:
        Каноническое название региона.
    """
    prompt = ('Введите название региона (или "{0}", чтобы увидеть список): '
              .format(HELP_COMMAND))
    while True:
        answer = ask_text(prompt)
        if answer == HELP_COMMAND:
            console_output.print_regions(regions)
            continue

        try:
            return stats.find_region(regions, answer)
        except ValueError as error:
            console_output.print_error(error)
            hints = stats.suggest_regions(regions, answer)
            if hints:
                console_output.print_info(
                    'Возможно, вы имели в виду: {0}'.format(', '.join(hints)))
            else:
                console_output.print_info(
                    'Введите "{0}", чтобы посмотреть полный список.'
                    .format(HELP_COMMAND))


def ask_column(columns, numeric_columns):
    """Запрашивает ID колонки для расчёта метрик.

    Args:
        columns: Список всех колонок файла.
        numeric_columns: Список числовых колонок.

    Returns:
        Имя выбранной колонки.

    Raises:
        ValueError: Если в файле нет ни одной числовой колонки.
    """
    if not numeric_columns:
        raise ValueError(
            'в файле нет ни одной числовой колонки, метрики посчитать нельзя')

    prompt = 'Введите ID колонки (от 1 до {0}): '.format(len(columns))
    while True:
        answer = ask_text(prompt)
        if not answer:
            console_output.print_error('ID колонки не может быть пустым')
            continue

        try:
            column_id = int(answer)
        except ValueError:
            console_output.print_error(
                '"{0}" — не целое число, введите ID из таблицы выше'
                .format(answer))
            continue

        if not 1 <= column_id <= len(columns):
            console_output.print_error(
                'ID должен быть в диапазоне от 1 до {0}, получено {1}'
                .format(len(columns), column_id))
            continue

        column = columns[column_id - 1]
        if column not in numeric_columns:
            console_output.print_error(
                'колонка "{0}" не числовая, метрики по ней посчитать нельзя'
                .format(column))
            console_output.print_info(
                'Доступные числовые колонки: {0}'
                .format(', '.join(numeric_columns)))
            continue
        return column


def ask_yes_no(prompt):
    """Запрашивает ответ "да"/"нет".

    Args:
        prompt: Текст вопроса.

    Returns:
        True для утвердительного ответа, False — для отрицательного.
    """
    while True:
        answer = ask_text('{0} (д/н): '.format(prompt)).lower()
        if answer in _YES_ANSWERS:
            return True
        if answer in _NO_ANSWERS:
            return False
        console_output.print_error(
            'ответ "{0}" не распознан, введите "д" или "н"'.format(answer))
