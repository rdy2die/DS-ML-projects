import math


def get_max(data):
    return max(data)


def get_min(data):
    return min(data)


def get_average(data):
    return sum(data) / len(data)


def get_median(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        median = sorted_data[n // 2]
    return median


def percentile(data, percent):
    if percent == 0:
        return min(data)
    sorted_data = sorted(data)
    index = math.ceil(len(sorted_data) * percent / 100) - 1
    return sorted_data[index]


def create_table(data):
    per_list = []
    for i in range(0, 101, 5):
        per_list.append((i, percentile(data, i)))
    return per_list
