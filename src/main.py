from src.test_main import domain_extraction


def ga(execution_path, boundary_delta, input_path, input_file, func, output_path):
    new = domain_extraction(input_path, input_file, func, output_path)
    # # Run GA
    # dom_point = new.GA(execution_path, algorithm_parameters={'test_budget': 100})
    # # Run GA_Local
    dom_point = new.GA_Local(execution_path, boundary_delta, algorithm_parameters={'test_budget': 100})

    return dom_point


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    input_path = r"G:\Domain_GA\src\sut"
    output_path = r"G:\Domain_GA\experiments"

    input_file = "equation1.py"
    func = "equation1"
    execution_path = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    boundary_delta = 1.5

    # input_file = "equation8.py"
    # func = "equation8"
    # execution_path = [1, 2, 3, 4, 5, 6, 0]
    # boundary_delta = 0.3

    # input_file = "equation3.py"
    # func = "equation3"
    # execution_path = [1, 2, 3, 5, 6, 7, 0]
    # boundary_delta = 0.5
    # -2,2 -3,3

    # input_file = "equation4.py"
    # func = "equation4"
    # execution_path = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    # boundary_delta = 0.5
    # # -8,8 -3,7

    # input_file = "equation7.py"
    # func = "equation7"
    # execution_path = [1, 2, 3, 4, 0]
    # boundary_delta = 1
    # -3,3 -4,4

    # input_file = "equation9.py"
    # func = "equation9"
    # execution_path = [1, 2, 3, 0]
    # boundary_delta = 1
    # 1,4 1,6

    # input_file = "equation5.py"
    # func = "equation5"
    # execution_path = [1, 2, 3, 4, 5, 7, 8, 0]
    # boundary_delta = 1
    # -1,5 -1,1


    # input_file = "equation6.py"
    # func = "equation6"
    # execution_path = [1, 2, 3, 0]
    # boundary_delta = 0.5

    # input_file = "equation10.py"
    # func = "equation10"
    # execution_path = [1, 2, 3, 4, 5, 0]
    # boundary_delta = 1.5
    # -10,10 -10,10

    # input_file = "equation11.py"
    # func = "equation11"
    # execution_path = [1, 2, 3, 4, 5, 6, 0]
    # boundary_delta = 0.5
    # -5,5 -5,5

    # input_file = "beam.py"
    # func = "beam"
    # execution_path = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0]
    # boundary_delta = 0.001

    # input_file = "bmi.py"
    # func = "bmi"
    # execution_path = [1, 2, 3, 4, 0]
    # boundary_delta = 1.5

    # test_gammaq(-2.655128168006236)
    # input_file = "expint.py"
    # func = "expint"
    # execution_path = [1, 2, 3, 4, 5, 6, 7, 10, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 0]
    # boundary_delta = 0

    # input_file = "gammaq.py"
    # func = "gammaq"
    # execution_path = [1, 2, 3, 5, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 48, 34, 35, 36, 37, 38, 39,
    #      40, 41, 42, 48, 34, 49, 0]
    # execution_path = [1, 2, 3, 5, 6, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 16, 17, 18, 19, 20, 22, 16, 23, 0]

    # input_file = "gcd.py"
    # func = "gcd"
    # execution_path = [1, 2, 3, 6, 7, 6, 7, 8, 6, 9, 0]

    # input_file = "bisection.py"
    # func = "bisection"
    # # execution_path = [1, 2, 4, 5, 6, 7, 9, 10, 5, 6, 7, 9, 10, 5, 13, 0]
    # execution_path = [1, 2, 4, 5, 6, 7, 9, 12, 5, 6, 7, 9, 10, 5, 13, 0]
    # boundary_delta = 0.1

    # input_file = "p11.py"
    # func = "p11"
    # execution_path = [1, 2, 3, 4, 5, 0]
    # boundary_delta = 1

    # input_file = "p18.py"
    # func = "p18"
    # execution_path = [1, 2, 3, 0]
    # boundary_delta = 1

    # input_file = "p2.py"
    # func = "p2"
    # execution_path = [1, 2, 3, 4, 5, 0]
    # boundary_delta = 1
    # input_file = "p5.py"
    # func = "p5"
    # execution_path = [1, 2, 3, 0]
    # boundary_delta = 1

    # input_file = "equation9.py"
    # func = "equation9"
    # # [1, 2, 3, 4, 5, 6, 0]
    # # [1, 2, 0]
    # execution_path = [1, 2, 3, 0]  # [1, 2, 3, 4, 5, 6, 7, 0]
    # boundary_delta = 0.5

    # input_file = "equation2.py"
    # func = "equation2"
    # execution_path = [1, 2, 3, 4, 5, 6, 0]
    # boundary_delta = 0.5
    # output_path = r"D:\evo-domain\experiments"

    # output_path = r"D:\evo-domain\experiments"

    # # output_path = r"D:\evo-domain\experiments"

    # input_file = "equation7.py"
    # func = "equation7"
    # # [1, 2, 3, 4, 5, 6, 0]
    # # [1, 2, 0]
    # execution_path = [1, 2, 3, 4, 0]
    # boundary_delta = 1
    # output_path = r"D:\evo-domain\experiments"

    ga(execution_path, boundary_delta, input_path, input_file, func, output_path)
