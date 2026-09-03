from math import sqrt


def beckerLago(x1:float, x2:float):
    if ((-5 + sqrt(sqrt(x1)))*(-5 + sqrt(sqrt(x1))) + (-5 + sqrt(sqrt(x2)))*(-5 + sqrt(sqrt(x2)))) <= 0:
        return 1
    else:
        return 0