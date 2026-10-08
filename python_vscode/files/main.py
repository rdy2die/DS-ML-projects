"""Лабораторная работа №1 «Знакомство с Python».

Консольная программа для расчёта статистических метрик набора данных
(демография регионов России, russian_demography.csv).

Точка входа. Модуль только связывает компоненты между собой и перехватывает
ошибки верхнего уровня: расчёты живут в stats, ввод-вывод — в csv_reader,
user_input и console_output.

Запуск:
    python main.py
    python main.py russian_demography.csv
"""

import sys

import console_output
import csv_reader
import stats
import user_input

# Имя колонки, по которой выполняется фильтрация набора данных.
REGION_COLUMN = 'region'

# Коды завершения программы.
_EXIT_OK = 0
_EXIT_ERROR = 1
_EXIT_INTERRUPTED = 130


def load_dataset(argv):
    """Загружает набор данных: путь берётся из аргументов или у пользователя.

    При ошибке чтения пользователю показывается причина, и путь
    запрашивается повторно.

    Args:
        argv: Список аргументов командной строки без имени скрипта.

    Returns:
        Кортеж (columns, rows, path).
    """
    path = argv[0] if argv else None
    while True:
        if not path:
            path = user_input.ask_file_path()
        try:
            columns, rows = csv_reader.read_csv(path)
            console_output.print_info(
                'Файл загружен: {0} строк, {1} колонок.'
                .format(len(rows), len(columns)))
            return columns, rows, path
        except ValueError as error:
            console_output.print_error(error)
            console_output.print_info('Укажите путь к файлу ещё раз.')
            path = None


def analyze(columns, rows, regions, numeric_columns):
    """Выполняет один цикл анализа: регион, колонка, метрики, перцентили.

    Args:
        columns: Список всех колонок файла.
        rows: Все строки набора данных.
        regions: Список доступных регионов.
        numeric_columns: Список числовых колонок.

    Raises:
        ValueError: Если данные выбранного среза не позволяют посчитать
            метрики (сообщение предназначено пользователю).
    """
    region = user_input.ask_region(regions)
    region_rows = stats.filter_by_region(rows, REGION_COLUMN, region)
    console_output.print_region_table(columns, region_rows, region)

    console_output.print_columns(columns, numeric_columns)
    column = user_input.ask_column(columns, numeric_columns)

    values, skipped = stats.extract_values(region_rows, column)
    console_output.print_metrics(column, stats.calculate_metrics(values),
                                 skipped)
    console_output.print_percentiles(
        column, stats.calculate_percentile_table(values))


def run(argv):
    """Запускает основной сценарий работы программы.

    Args:
        argv: Список аргументов командной строки без имени скрипта.

    Returns:
        Код завершения программы.
    """
    print('Статистика демографических показателей регионов России')

    columns, rows, _ = load_dataset(argv)

    try:
        regions = stats.get_regions(rows, REGION_COLUMN)
    except ValueError as error:
        console_output.print_error(error)
        console_output.print_info(
            'Найденные колонки: {0}'.format(', '.join(columns)))
        return _EXIT_ERROR

    if not regions:
        console_output.print_error(
            'в колонке "{0}" нет ни одного заполненного значения'
            .format(REGION_COLUMN))
        return _EXIT_ERROR

    numeric_columns = stats.get_numeric_columns(rows, columns)
    if not numeric_columns:
        console_output.print_error(
            'в файле нет ни одной числовой колонки, метрики посчитать нельзя')
        return _EXIT_ERROR

    while True:
        try:
            analyze(columns, rows, regions, numeric_columns)
        except ValueError as error:
            console_output.print_error(error)

        if not user_input.ask_yes_no('\nВыполнить ещё один расчёт?'):
            print('\nРабота завершена.')
            return _EXIT_OK


def main():
    """Обрабатывает ошибки верхнего уровня и возвращает код возврата.

    Returns:
        Код завершения программы.
    """
    try:
        return run(sys.argv[1:])
    except KeyboardInterrupt:
        print('\n\nРабота прервана пользователем (Ctrl+C).')
        return _EXIT_INTERRUPTED
    except EOFError:
        print('\n\nВвод завершён (Ctrl+D), программа остановлена.')
        return _EXIT_INTERRUPTED
    except RecursionError as error:
        console_output.print_error(
            'превышена глубина рекурсии: {0}'.format(error))
        return _EXIT_ERROR
    except MemoryError:
        console_output.print_error(
            'не хватает оперативной памяти для обработки файла')
        return _EXIT_ERROR
    except OSError as error:
        console_output.print_error(
            'ошибка операционной системы: {0}'.format(error))
        return _EXIT_ERROR
    except Exception as error:  # pylint: disable=broad-except
        # Страховка: программа не должна «падать» со стек-трейсом.
        console_output.print_error(
            'непредвиденная ошибка ({0}): {1}'
            .format(type(error).__name__, error))
        return _EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())
