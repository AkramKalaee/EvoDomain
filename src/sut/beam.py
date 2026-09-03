def beam(x: float, y: float):
    It = (x ** 3 * y + x * y ** 3) / 12
    Iz = x ** 3 * y / 12
    Ik = x * y ** 3 / 12
    Iy = (86.65 * It * 216.62 * Iz / (1 - .27 ** 2))
    if x * y <= 0.0025:
        if 5 * .5 ** 3 / (3 * 216620 * Ik) <= 5:
            if 6 * 5 * .5 / (x * y ** 2) <= 240000:
                if 3 * 5 / (2 * x * y) <= 120000:
                    if y / x <= 10:
                        if x / y <= 10:
                            if 4 / .5 ** 2 * Iy ** .5 >= 2 * 5 / 1e6:
                                return True