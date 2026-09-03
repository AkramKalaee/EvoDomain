def equation3(x: float, y: float):
    X = (x ** 2)
    Y = (y ** 2)

    if Y + 2 * x >= 1.5 * X + 1:
        if Y + 2 * X <= 2 * x + 4.25:
            return 1
    return 0
