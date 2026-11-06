"""Лабораторная работа: интерполяция функции.

Программа:
    1. запрашивает функцию f(x), границы отрезка и шаг;
    2. вычисляет по ним узлы интерполяции;
    3. строит график исходной функции и трёх собственных
       интерполяций (линейной, кусочно-квадратичной, квадратичной);
    4. в цикле принимает с клавиатуры x, проверяет, что он лежит
       внутри известного интервала, и выводит интерполированные
       значения, точное значение f(x) и погрешность каждого метода.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

from my_interpolation import METHODS

# Имена, которые можно использовать в формуле функции.
# __builtins__ отключены, поэтому через eval нельзя вызвать
# ничего, кроме математики numpy.
ALLOWED_NAMES = {
    name: getattr(np, name)
    for name in ("sin", "cos", "tan", "exp", "log", "sqrt", "abs",
                 "arctan", "sinh", "cosh", "pi", "e")
}


def make_function(expression):
    """Превращает строку вида 'sin(x) * x' в функцию f(x)."""
    code = compile(expression, "<function>", "eval")

    def f(x):
        return eval(code, {"__builtins__": {}}, {**ALLOWED_NAMES, "x": x})

    f(np.array([1.0]))  # пробный вызов: ошибка в формуле видна сразу
    return f


def read_float(prompt, default):
    """Читает число; при пустом вводе возвращает значение по умолчанию."""
    text = input(f"{prompt} [{default}]: ").strip()
    return float(text) if text else default


def read_settings():
    """Запрашивает у пользователя функцию, отрезок и шаг."""
    expression = input("Функция f(x) [sin(x) * x]: ").strip() or "sin(x) * x"
    f = make_function(expression)
    a = read_float("Начало отрезка a", 0.0)
    b = read_float("Конец отрезка b", 10.0)
    step = read_float("Шаг между узлами", 1.0)
    if a >= b or step <= 0:
        raise ValueError("Нужно a < b и шаг > 0")
    xs = np.arange(a, b + step / 2, step)  # + step/2 — чтобы b вошло
    if len(xs) < 3:
        raise ValueError("Слишком большой шаг: нужно минимум 3 узла")
    return expression, f, xs, f(xs)


def plot(expression, f, xs, ys):
    """Рисует функцию, узлы и все интерполяции на одном графике."""
    dense = np.linspace(xs[0], xs[-1], 1000)
    plt.figure(figsize=(11, 6))
    plt.plot(dense, f(dense), "k-", linewidth=2.5, label=f"f(x) = {expression}")
    for name, method in METHODS.items():
        plt.plot(dense, method(xs, ys, dense), "--", label=name)
    scipy_quad = interp1d(xs, ys, kind="quadratic")
    plt.plot(dense, scipy_quad(dense), ":", label="SciPy quadratic (для сравнения)")
    plt.plot(xs, ys, "ro", label="Узлы интерполяции")
    plt.title("Сравнение методов интерполяции")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show(block=False)
    plt.pause(0.1)  # даём окну отрисоваться до ввода в консоли


def query_loop(f, xs, ys):
    """Принимает x с клавиатуры и печатает результаты интерполяции."""
    print(f"\nИзвестный интервал: [{xs[0]}, {xs[-1]}]. Пустой ввод — выход.")
    while True:
        text = input("\nВведите x: ").strip()
        if not text:
            break
        try:
            x = float(text)
        except ValueError:
            print("Это не число.")
            continue
        if not xs[0] <= x <= xs[-1]:
            print("Точка вне интервала — интерполяция невозможна.")
            continue
        exact = float(f(np.array(x)))
        print(f"Точное значение f(x) = {exact:.6f}")
        for name, method in METHODS.items():
            value = float(method(xs, ys, np.array(x)))
            print(f"  {name:32} {value:12.6f}   погрешность {abs(value - exact):.2e}")


def main():
    expression, f, xs, ys = read_settings()
    plot(expression, f, xs, ys)
    query_loop(f, xs, ys)


if __name__ == "__main__":
    main()
