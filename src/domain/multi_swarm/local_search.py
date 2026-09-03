import copy
import math
import random

from domain.Boundary import boundary_points
from domain.multi_swarm.incremental_svclustering import isvc
import numpy


def hill_climbing_v1(current_sol, current_fitness, delta, N, evaluate_function):
    pool = []
    i = 0
    c = numpy.array(current_sol)
    while i < N:
        # new_sample = np.random.uniform(start, end)
        new_sample = numpy.random.uniform(c - delta, c + delta)
        if numpy.linalg.norm(new_sample - c) <= delta:
            pool.append(new_sample.tolist())
            i += 1
    print('pool generated!')
    best_fit = current_fitness
    best_candidate = copy.deepcopy(current_sol)
    for i in range(N):
        print('candidate ', i)
        # candidate = Individual()
        # candidate.variables = pool[i]
        candidate = pool[i]
        candidate_fitness = evaluate_function(candidate)[0]
        if candidate_fitness < best_fit or candidate_fitness == 0:
            best_fit = candidate_fitness
            best_candidate = copy.deepcopy(candidate)

    return best_candidate, (best_fit,)


def hill_climbing(current_sol, current_fitness, delta, N, evaluate_function):
    pool = []
    i = 0
    c = numpy.array(current_sol)
    best_fit = current_fitness
    best_candidate = copy.deepcopy(current_sol)
    while i < N:
        # new_sample = np.random.uniform(start, end)
        new_sample = numpy.random.uniform(c - delta, c + delta)
        if numpy.linalg.norm(new_sample - c) <= delta:
            candidate = new_sample.tolist()
            i += 1
            print('candidate ', i)
            candidate_fitness = evaluate_function(candidate)[0]
            if candidate_fitness < best_fit or candidate_fitness == 0:
                print('set candidate ', i)
                best_fit = candidate_fitness
                best_candidate = copy.deepcopy(candidate)
                c = numpy.array(candidate)

    return best_candidate, (best_fit,)


def boundary_identifier(current_sol, current_fitness, delta, N, evaluate_function, vartype, varbound):
    boundary_identifier = boundary_points(current_sol, current_fitness, vartype, varbound,
                                          evaluate_function, algorithm_parameters={"length": [10, 20], "budget": N})
    candidates = boundary_identifier.run_boundary_point(delta)
    return boundary_identifier.test_data


def find_boundary(tc, fit, label, L, alfa, a, evaluate_function):
    import time
    timee = 5
    test_mode = "time"
    begin = time.time()
    boundary_list = []
    retracted_points = []
    non_retracted_points = []
    print(tc)
    # primepath.append(tc)
    tb = []
    # path2 = config.global_config['target_path']
    t = 0
    flag = False
    t = 0
    qq = tc
    qq_fit = fit
    while t < 10:
        t += 1
        if len(tc) == 2:
            tc = calculate_tc_alfa(qq, tc, L, alfa, a, t)
        else:
            tc = calculate_tc_alfa(qq, tc, L, alfa, a, t, flag)
            print(tc)
        print((time.time() - begin))
        # if test_mode == "time" and float(time.time() - begin) / 60 > timee:
        #     return "stop"
        # path1, res, tr = coverage_eval.path_coverage(tc)
        candidate_fitness, label = evaluate_function(tc)
        candidate_fitness = candidate_fitness[0]
        # demand_TD_siza=demand_TD_siza+-1
        if candidate_fitness != 0:
            print(":(")
            L = L / 2
            if flag is False:
                alfa = -alfa
            flag = True
            retracted_points.append(tc)
        else:
            print(":)")
            # primepath.append(tc)
            tb = tc
            qq = tc
            print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWwwwww")
            boundary_list.append([tb, (candidate_fitness,), label])
            if flag is True:
                L = L / 2
                alfa = -alfa
                flag = False
                non_retracted_points.append(tc)

    if len(boundary_list) > 0:
        print('*****************len(boundary_list)********************', len(boundary_list))
        return boundary_list
    else:
        return [[qq, (qq_fit,), label]]


def calculate_tc_alfa(qq, tc, l, alfa, a, t, flag=True):
    if (len(tc) == 2):
        l = alfa * l
        print(l)
        we = []
        x = l * math.cos(a) + tc[0]
        y = l * math.sin(a) + tc[1]
        we.append(x)
        we.append(y)

        print(we)
        return we
    else:
        if t == 1:
            while True:
                x = [random.uniform(78, 102), random.uniform(33, 45), random.uniform(27, 45),
                     random.uniform(27, 45), random.uniform(27, 45)]
                if (math.dist(tc, x)) > l and (math.dist(tc, x)) < l + 1:
                    return x
        else:
            if flag == True:
                print("ffffffffffffff")
                arr_mid = []
                for i in range(len(tc)):
                    arr_mid.append(float(tc[i] + qq[i]) / 2)
                return arr_mid
            else:
                while True:
                    x = [random.uniform(78, 102), random.uniform(33, 45), random.uniform(27, 45),
                         random.uniform(27, 45), random.uniform(27, 45)]
                    if (math.dist(tc, x)) > l and (math.dist(tc, x)) < l + 1:
                        return x


def generate_random_point(l, n, tc):
    a = []
    for i in range(0, n):
        r = random.random()
        r = r * 360

        x = l * math.cos(r) + tc[0]
        y = l * math.sin(r) + tc[1]
        a.append([x, y, r])

    return a


def local_search(tc, current_fitness, label, delta, N, evaluate_function):
    primepath = []
    retracted_points = []
    non_retracted_points = []
    boundary_list = []
    demand_TD_siza = 100

    time_budget = 5
    test_mode = "time"  # sample or  time

    alfa = 1
    #############################################################config  #################################333
    # tc = [78.55933306935277, 34.25708115772749, 34.796602734548614, 31.084545219732796,
    #       42.83111794806186]  # init prime
    # random_arr=[[]]
    l = 30  # len of des
    timee = 5  # iteration of loop for each boundary
    N = 1000  # number of boundary
    dim = 2  # dimention
    import time
    begin = time.time()

    primepath.append(tc)

    if dim == 2:
        for i in range(0, N):
            r = random.uniform(0, 360)
            restults = find_boundary(tc,current_fitness, label, l, alfa, r, evaluate_function)
            boundary_list.extend(restults)
    else:
        for i in range(0, N):
            we = find_boundary(tc,current_fitness, label, l, alfa, 0, evaluate_function)
            if we == "stop":
                break
        # plot_boundary.plot(primepath)

        print("boundarys =", boundary_list)

    time.sleep(1)
    end = time.time()
    print("time=======>         ", (end - begin), "        <==========time")

    idx = random.choice(range(len(boundary_list)))
    return (*boundary_list[idx],)

    # from csv import writer
    #
    # with open(r'output_eval_baseline/boundary_points.csv', 'w') as f_object:
    #     for oo in range(0, len(boundary_list)):
    #         rows = boundary_list[oo]
    #
    #         writer_object = writer(f_object)
    #
    #         # Pass the list as an argument into
    #         # the writerow()
    #         writer_object.writerow(rows)
    #
    #     # Close the file object
    #     f_object.close()
    #     rows.clear()
    # from csv import writer
    #
    # with open(r'output_eval_baseline/testdata.arrf', 'w') as f_object:
    #     for oo in range(0, len(primepath)):
    #         rows = primepath[oo]
    #
    #         writer_object = writer(f_object)
    #
    #         # Pass the list as an argument into
    #         # the writerow()
    #         writer_object.writerow(rows)
    #
    #     # Close the file object
    #     f_object.close()
    #     rows.clear()
    # from csv import writer
    #
    # with open(r'output_eval_baseline/eval.txt', 'w') as f_object:
    #
    #     rows = ["time: ", end - begin]
    #     rows += ["# size TD demand:", ]
    #
    #     writer_object = writer(f_object)
    #
    #     # Pass the list as an argument into
    #     # the writerow()
    #     writer_object.writerow(rows)
    #
    #     # Close the file object
    #     f_object.close()
    #     rows.clear()


# def binary_search(self, x, y, sec, genenictime, boundary_time_start, time_budget, counter_prime_passed,
#                   counter_test_data_not_passed):
#     a = x
#     b = y
#
#     if sec == 1:
#         a = norm_lable(x)
#         b = norm_lable(y)
#
#     while (True):
#         c = distance_calculate.cal_middle_ponit(a, b)
#         print("middle", c)
#         path2 = config.global_config['target_path']
#         print("@@@####   ", (len(counter_prime_passed) + len(counter_test_data_not_passed)))
#         len_demand_boundary = len(counter_prime_passed) + len(counter_test_data_not_passed)
#         if (config.global_config['test_budget'] != 'time' and (len_demand_boundary > budget_sample_BA)) or (
#                 config.global_config['test_budget'] == 'time' and (
#                 ((time.time() - boundary_time_start) / 60) + genenictime) > time_budget):
#             return 'end_budget'
#
#         path1, res, tr = coverage_eval.path_coverage(c)  # for function test
#         if path1 == path2:
#             print("prime passed@@@@@@@@@@@@@@@@@@,", c)
#             a = c
#             counter_prime_passed.append(a)
#         else:
#             b = c
#             counter_test_data_not_passed.append(b)
#         dist = distance_calculate.distans_two_point(a, b)
#         if dist < 0.001:
#             break
#     return a