import numpy as np


def hosaki(x1: float, x2: float):
    p = (1 + 7 * x1 * x1 - 8 * x1 - 2.33333333333333 * x1)
    q = (x1 * x1 + 0.25 * x1 * x1 * x1 * x1)
    i = p * q
    j = np.exp(-x2)
    k = i * x2 * x2
    if k * j <= 0:
        return True
    return False
