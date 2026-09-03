import math


def equation8(x: float, y: float):
    k = math.exp(x + y) - 1
    h = math.sin((x)) + 1.9 * math.cos((y)) + 1
    if k < 0:
        if h <= 0:
            return True
