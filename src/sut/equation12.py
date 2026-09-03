import math


def equation12(x: float, y: float, z: float):
    k = math.sin(10*(x ** 2 + y ** 2)) / 10
    if k < 5:
        h = pow(z, 2)
        if h + k < 1.4:
            return True
