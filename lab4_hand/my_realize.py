import numpy as np


def linear_interpolation(x_nodes, y_nodes, x):
    if x < x_nodes[0] or x > x_nodes[-1]:
        raise ValueError(f"Error value")
    for i in range(len(x_nodes) - 1):
        if x_nodes[i] <= x <= x_nodes[i + 1]:
            fraction = (x - x_nodes[i]) / (x_nodes[i + 1] - x_nodes[i])
            y_res = y_nodes[i] + (y_nodes[i + 1] - y_nodes[i]) * fraction
            return y_res


def quad_interpolation(x_nodes, y_nodes, x):
    """
    Собственная реализация квадратичной интерполяции (полином Лагранжа 2-й степени).
    Использует скользящее окно из 3 ближайших узлов.
    """
    x_nodes = np.asarray(x_nodes, dtype=float)
    y_nodes = np.asarray(y_nodes, dtype=float)

    # 1. Проверка выхода за границы
    if x < x_nodes[0] or x > x_nodes[-1]:
        raise ValueError(f"Точка {x} вне границ интервала!")

    n = len(x_nodes)

    # 2. Находим индекс узла, ближайшего к x
    min_dist = float("inf")
    idx = 0
    for i in range(len(x_nodes)):
        dist = abs(x_nodes[i] - x)
        if dist < min_dist:
            min_dist = dist
            idx = i

    # 3. Формируем скользящее окно из 3 точек с защитой от вылета за границы
    if idx == 0:
        i0, i1, i2 = 0, 1, 2
    elif idx == n - 1:
        i0, i1, i2 = n - 3, n - 2, n - 1
    else:
        if x < x_nodes[idx]:
            i0, i1, i2 = idx - 2, idx - 1, idx
        else:
            i0, i1, i2 = idx - 1, idx, idx + 1

    # Жесткая страховка индексов окна
    i0 = max(0, min(i0, n - 3))
    i1 = i0 + 1
    i2 = i0 + 2

    x0, x1, x2 = x_nodes[i0], x_nodes[i1], x_nodes[i2]
    y0, y1, y2 = y_nodes[i0], y_nodes[i1], y_nodes[i2]

    # 4. Вычисление базисных полиномов Лагранжа 2-й степени
    l0 = ((x - x1) * (x - x2)) / ((x0 - x1) * (x0 - x2))
    l1 = ((x - x0) * (x - x2)) / ((x1 - x0) * (x1 - x2))
    l2 = ((x - x0) * (x - x1)) / ((x2 - x0) * (x2 - x1))

    # 5. Искомое значение y
    y_res = y0 * l0 + y1 * l1 + y2 * l2
    return y_res


def cubic_interpolation(x_nodes, y_nodes, x):
    """
    Собственная реализация кубической интерполяции (полином Лагранжа 3-й степени).
    Использует скользящее окно из 4 ближайших узлов.
    """
    x_nodes = np.asarray(x_nodes, dtype=float)
    y_nodes = np.asarray(y_nodes, dtype=float)
    
    # 1. Проверка выхода за границы
    if x < x_nodes[0] or x > x_nodes[-1]:
        raise ValueError(f"Точка {x} вне границ интервала!")
        
    n = len(x_nodes)
    
    # 2. Находим индекс узла, ближайшего к x
    min_dist = float("inf")
    idx = 0
    for i in range(n):
        dist = abs(x_nodes[i] - x)
        if dist < min_dist:
            min_dist = dist
            idx = i
            
    # 3. Формируем скользящее окно из 4 точек с защитой от вылета за границы
    if idx <= 1:
        i0, i1, i2, i3 = 0, 1, 2, 3
    elif idx >= n - 2:
        i0, i1, i2, i3 = n - 4, n - 3, n - 2, n - 1
    else:
        if x < x_nodes[idx]:
            i0, i1, i2, i3 = idx - 3, idx - 2, idx - 1, idx
        else:
            i0, i1, i2, i3 = idx - 2, idx - 1, idx, idx + 1
            
    # Жесткая страховка индексов окна (для 4 точек)
    i0 = max(0, min(i0, n - 4))
    i1 = i0 + 1
    i2 = i0 + 2
    i3 = i0 + 3
    
    x0, x1, x2, x3 = x_nodes[i0], x_nodes[i1], x_nodes[i2], x_nodes[i3]
    y0, y1, y2, y3 = y_nodes[i0], y_nodes[i1], y_nodes[i2], y_nodes[i3]
    
    # 4. Вычисление базисных полиномов Лагранжа 3-й степени
    l0 = ((x - x1) * (x - x2) * (x - x3)) / ((x0 - x1) * (x0 - x2) * (x0 - x3))
    l1 = ((x - x0) * (x - x2) * (x - x3)) / ((x1 - x0) * (x1 - x2) * (x1 - x3))
    l2 = ((x - x0) * (x - x1) * (x - x3)) / ((x2 - x0) * (x2 - x1) * (x2 - x3))
    l3 = ((x - x0) * (x - x1) * (x - x2)) / ((x3 - x0) * (x3 - x1) * (x3 - x2))
    
    # 5. Искомое значение y
    y_res = y0 * l0 + y1 * l1 + y2 * l2 + y3 * l3
    return y_res