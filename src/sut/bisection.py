"""
Given a function on floating number f(x) and two floating numbers ‘a’ and ‘b’ such that
f(a) * f(b) < 0 and f(x) is continuous in [a, b].
Here f(x) represents algebraic or transcendental equation.
Find root of function in interval [a, b] (Or find a value of x such that f(x) is 0)

https://en.wikipedia.org/wiki/Bisection_method
"""
def bisection(a: float, b: float) -> float:
    if equation(a) * equation(b) >= 0:
        return "Wrong space!"
    c = a
    while (b - a) >= 0.01:
        c = (a + b) / 2
        if equation(c) == 0.0:
            break
        if equation(c) * equation(a) < 0:
            b = c
        else:
            a = c
    return c


def equation(x: float) -> float:
    return 10 - x * x
