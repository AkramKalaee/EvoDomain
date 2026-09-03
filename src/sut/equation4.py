import math


def equation4(x: float, y: float):
    r1 = 2.3
    r2 = 100
    r3 = 64
    k = math.sqrt(r2 ** 2 - x ** 2)
    m = math.sqrt(r3 ** 2 - x ** 2)
    if x ** 2 + y ** 2 <= r1 ** 2 or (k <= y <= m):
        return 1
    return 0
