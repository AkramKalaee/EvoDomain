import math

def equation5(x:float, y:float):
    k1 = math.exp((-math.fabs(x) - math.fabs(y)))
    k2 = math.exp((-math.fabs(x - 4) - math.fabs(y)))
    k3 = math.exp(-math.fabs(x + 10) - math.fabs(y - 5))
    k4 = math.sin(2 * x * y)

    if -10 * k1 - 7 * k2 - 19 * k3 + k4 + 5 <= 0:
        return 1
    return 0
