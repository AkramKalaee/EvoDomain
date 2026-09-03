def equation2(x: float, y: float, z: float):
    k = x ** 2 + y ** 2
    if k < 5:
        h = pow(z, 2)
        if h + k < 1.4:
            return True
