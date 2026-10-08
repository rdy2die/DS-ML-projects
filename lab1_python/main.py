"""Точка входа: диалог с пользователем.

Вся арифметика — в stats_logic, всё чтение и печать таблицы — в io_layer.
Здесь только вопросы пользователю и вывод готовых результатов.
"""

from errors import (
    AppError,
    ChoiceError,
    ColumnNotFoundError,
    MenuIndexError,
    NoMetricColumnsError,
    NoRegionsError,
    RegionNotFoundError,
)
from io_layer import REGION_COLUMN, print_rows_table, read_dataset
from stats_logic import (
    collect_regions,
    create_table,
    extract_values,
    filter_by_region,
    get_average,
    get_max,
    get_median,
    get_min,
)

PRECISION = 2
MENU_START_INDEX = 1
EXIT_COMMAND = "exit"
YES_ANSWERS = ("y", "yes")
NO_ANSWERS = ("n", "no")
EXIT_MESSAGE = "Работа программы завершена."


def format_number(value):
    return f"{value:.{PRECISION}f}"


def show_error(error):
    """Единая точка вывода ошибки пользователю."""
    print(f"Ошибка: {error}")


def ask_dataset():
    """Спрашивать путь, пока не прочитается корректный файл.

    Возвращает (строки, колонки) или None, если пользователь ввёл exit.
    """
    while True:
        path = input(
            f"Введите путь до файла (или '{EXIT_COMMAND}' для выхода): "
        ).strip()
        if path.lower() == EXIT_COMMAND:
            return None
        try:
            return read_dataset(path)
        except AppError as error:
            show_error(error)


def resolve_choice(answer, options, not_found_error, what):
    """Превратить ответ пользователя в элемент списка.

    Принимает номер (ID) или название. Каждая причина отказа —
    своё исключение, текст формируется здесь, где есть контекст.
    """
    if answer.isdigit():
        number = int(answer)
        last_index = MENU_START_INDEX + len(options) - 1
        if MENU_START_INDEX <= number <= last_index:
            return options[number - MENU_START_INDEX]
        raise MenuIndexError(
            f"номера {number} нет в списке — допустимы "
            f"от {MENU_START_INDEX} до {last_index}."
        )

    if answer in options:
        return answer

    if not answer:
        raise not_found_error(
            f"вы ничего не ввели — нужен номер или название ({what})."
        )

    raise not_found_error(f"'{answer}' — такого пункта нет в списке ({what}).")


def choose_from_list(title, options, what, not_found_error):
    """Показать пронумерованный список и получить выбор пользователя.

    Возвращает выбранное значение или None, если пользователь ввёл exit.
    """
    print(f"\n{title}\n")
    for index, option in enumerate(options, start=MENU_START_INDEX):
        print(f"{index}. {option}")

    while True:
        answer = input(
            f"\nВведите {what} — номер или название (или '{EXIT_COMMAND}' для выхода): "
        ).strip()

        if answer.lower() == EXIT_COMMAND:
            return None

        try:
            return resolve_choice(answer, options, not_found_error, what)
        except ChoiceError as error:
            show_error(error)


def ask_continue():
    while True:
        answer = input("\nХотите продолжить? (y/n): ").strip().lower()
        if answer in YES_ANSWERS:
            return True
        if answer in NO_ANSWERS:
            return False
        print("Некорректный ввод. Введите 'y' или 'n'.")


def print_statistics(values):
    print(f"\nМаксимум: {format_number(get_max(values))}")
    print(f"Минимум: {format_number(get_min(values))}")
    print(f"Среднее: {format_number(get_average(values))}")
    print(f"Медиана: {format_number(get_median(values))}")

    print("\nПерцентили:")
    for percent, value in create_table(values):
        print(f"{percent}%: {format_number(value)}")


def prepare_options(all_rows, columns):
    """Списки для меню: регионы и числовые колонки."""
    regions = collect_regions(all_rows, REGION_COLUMN)
    if not regions:
        raise NoRegionsError(
            f"колонка '{REGION_COLUMN}' есть, но все её значения пустые."
        )

    metrics = [column for column in columns if column != REGION_COLUMN]
    if not metrics:
        raise NoMetricColumnsError(
            f"кроме '{REGION_COLUMN}' в файле нет ни одной колонки — считать нечего."
        )

    return regions, metrics


def run_once(all_rows, columns, regions, metrics):
    """Один цикл «выбрал регион и метрику — получил результат».

    Возвращает False, если пользователь решил выйти.
    """
    region = choose_from_list(
        "Выберите регион из списка:", regions, "регион", RegionNotFoundError
    )
    if region is None:
        return False

    metric = choose_from_list(
        "Выберите метрику из списка:", metrics, "метрику", ColumnNotFoundError
    )
    if metric is None:
        return False

    region_rows = filter_by_region(all_rows, REGION_COLUMN, region)

    try:
        values, skipped = extract_values(region_rows, metric)
    except AppError as error:
        show_error(f"по региону '{region}' — {error}")
        return ask_continue()

    if skipped:
        print(f"\nПредупреждение: пропущено {skipped} некорректных значений.")

    print()
    print_rows_table(region_rows, columns)
    print_statistics(values)

    return ask_continue()


def main():
    dataset = ask_dataset()
    if dataset is None:
        print(EXIT_MESSAGE)
        return

    all_rows, columns = dataset

    try:
        regions, metrics = prepare_options(all_rows, columns)
    except AppError as error:
        show_error(error)
        return

    while run_once(all_rows, columns, regions, metrics):
        pass

    print(EXIT_MESSAGE)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{EXIT_MESSAGE}")
