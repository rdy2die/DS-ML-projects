import csv
import sys

from errors import (
    AppError,
    DatasetContentError,
    EmptyResultError,
)
from io_layer import print_rows_table, validate_file
from stats_logic import create_table, get_average, get_max, get_median, get_min


def main():
    while True:
        path = input("Введите путь до файла: ").strip()
        try:
            validate_file(path)
            with open(path, encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                all_rows = list(reader)
                columns = reader.fieldnames
            if not columns or "region" not in columns:
                raise DatasetContentError("В файле нет обязательной колонки 'region'.")
            if not all_rows:
                raise DatasetContentError("Файл не содержит строк с данными.")
            break
        except AppError as error:
            print(f"Ошибка: {error}")
        except (OSError, UnicodeDecodeError) as error:
            print(f"Ошибка при чтении файла: {error}")

    regions = {row["region"] for row in all_rows if row["region"]}
    sorted_regions = sorted(regions)
    numeric_columns = [c for c in columns if c != "region"]

    while True:
        print("\nВыберите регион из списка:\n")
        for i, r in enumerate(sorted_regions, start=1):
            print(f"{i}. {r}")

        while True:
            input_region = input("\nВведите регион (или 'exit' для выхода): ").strip()
            if input_region.lower() == "exit":
                sys.exit("Работа программы завершена.")
            if input_region in regions:
                region = input_region
                break
            print(f"Ошибка: регион '{input_region}' не найден. Попробуйте снова.")

        region_rows = [row for row in all_rows if row["region"] == region]

        print("\nВыберите метрику из списка:\n")
        for i, c in enumerate(numeric_columns, start=1):
            print(f"{i}. {c}")

        while True:
            input_metric = input("\nВведите метрику (или 'exit' для выхода): ").strip()
            if input_metric.lower() == "exit":
                sys.exit("Работа программы завершена.")
            if input_metric in numeric_columns:
                metric = input_metric
                break
            print(f"Ошибка: метрика '{input_metric}' не найдена. Попробуйте снова.")

        values = []
        skipped = 0
        for row in region_rows:
            try:
                values.append(float(row[metric]))
            except (ValueError, TypeError):
                skipped += 1

        if skipped:
            print(f"Предупреждение: пропущено {skipped} некорректных значений.")

        try:
            if not values:
                raise EmptyResultError(
                    f"По региону '{region}' и метрике '{metric}' нет числовых данных."
                )
        except EmptyResultError as error:
            print(f"Ошибка: {error}")
            continue

        print()
        print_rows_table(region_rows, columns)

        print(f"\nМаксимум: {get_max(values):.2f}")
        print(f"Минимум: {get_min(values):.2f}")
        print(f"Среднее: {get_average(values):.2f}")
        print(f"Медиана: {get_median(values):.2f}")

        print("\nПерцентили:")
        for percent, value in create_table(values):
            print(f"{percent}%: {value:.2f}")

        while True:
            answer = input("\nХотите продолжить? (y/n): ").strip().lower()
            if answer in ("y", "yes"):
                break
            elif answer in ("n", "no"):
                sys.exit("Работа программы завершена.")
            else:
                print("Некорректный ввод. Введите 'y' или 'n'.")

if __name__ == "__main__":
    main()