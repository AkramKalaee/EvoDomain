import math
import sys
sys.path.append(r'G:\Domain_GA\src\instrument')
sys.path.append(r'G:\Domain_GA\src')
from src.runner import evaluate_branch_distance
from Coverage import cover_decorator

@cover_decorator
def equation1_instrumented(x: float, y: float):
    k = y ** 2
    h = math.sin(math.radians(x * 30))
    l = math.cos(math.radians(x * 40))
    if evaluate_branch_distance(1, [1, 'GtE', k, x * 10]):
        if evaluate_branch_distance(2, [1, 'LtE', y, h * 25]):
            if evaluate_branch_distance(3, [1, 'GtE', y, l * 15]):
                return True is True
