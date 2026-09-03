import math


def equation7(x: float, y: float):
    k = 2 * math.cos(x) + math.sin(4 * x)
    if k <= 4 * y + x ** 2 and y >= -4:
        return 1
    return 0
