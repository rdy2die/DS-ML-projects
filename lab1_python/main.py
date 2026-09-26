"""Точка входа: диалог с пользователем.

Вся арифметика — в stats_logic, всё чтение и печать таблицы — в io_layer.
Здесь только вопросы пользователю и вывод готовых результатов.
"""

from errors import AppError
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
            print(f"Ошибка: {error}")


def choose_from_list(title, options, what):
    """Выбор пункта по номеру (ID) или по названию.

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

        if answer.isdigit():
            number = int(answer)
            if MENU_START_INDEX <= number < MENU_START_INDEX + len(options):
                return options[number - MENU_START_INDEX]
            print(
                f"Ошибка: номера {number} нет в списке. "
                f"Допустимо от {MENU_START_INDEX} "
                f"до {len(options)}. Попробуйте снова."
            )
            continue

        if answer in options:
            return answer

        print(f"Ошибка: {what} '{answer}' не найдена. Попробуйте снова.")


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


def main():
    dataset = ask_dataset()
    if dataset is None:
        print(EXIT_MESSAGE)
        return

    all_rows, columns = dataset
    regions = collect_regions(all_rows, REGION_COLUMN)
    numeric_columns = [c for c in columns if c != REGION_COLUMN]

    if not regions:
        print(f"Ошибка: в колонке '{REGION_COLUMN}' нет значений.")
        return
    if not numeric_columns:
        print("Ошибка: кроме региона в файле нет ни одной колонки.")
        return

    while True:
        region = choose_from_list("Выберите регион из списка:", regions, "регион")
        if region is None:
            print(EXIT_MESSAGE)
            return

        metric = choose_from_list(
            "Выберите метрику из списка:", numeric_columns, "метрику"
        )
        if metric is None:
            print(EXIT_MESSAGE)
            return

        region_rows = filter_by_region(all_rows, REGION_COLUMN, region)

        try:
            values, skipped = extract_values(region_rows, metric)
        except AppError as error:
            print(f"\nОшибка: по региону '{region}' — {error}")
            if not ask_continue():
                print(EXIT_MESSAGE)
                return
            continue

        if skipped:
            print(f"\nПредупреждение: пропущено {skipped} некорректных значений.")

        print()
        print_rows_table(region_rows, columns)
        print_statistics(values)

        if not ask_continue():
            print(EXIT_MESSAGE)
            return


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{EXIT_MESSAGE}")
