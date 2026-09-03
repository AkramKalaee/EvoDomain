import math


def equation1(x: float, y: float):
    k = y ** 2
    h = math.sin(math.radians(x * 30))
    l = math.cos(math.radians(x * 40))
    if k >= x * 10:
        if y <= h * 25:
            if y >= l*15:
                return True
