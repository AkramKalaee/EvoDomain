import copy
import math

import numpy as np
import sys
import os
import csv
import pickle

from truths.truths import Gob

branch_distances_true = []
branch_distances_false = []

clause_distances_true = []
clause_distances_false = []


class run:
    def __init__(self, search_algorithm, algorithm_name, input_path, file_name, function_name,
                 output_path, source, prime_pathes, requirement, p_path, _boundary_delta, test_data,
                 algorithm_parameters):
        from src.test_tools import get_argument_and_type, pc_num_extract, line_true_false, and_or, dom_type
        self.algorithm = search_algorithm
        self.algorithm_name = algorithm_name
        self.algorithm_parameters = algorithm_parameters
        self.function_name = function_name
        self.output_path = output_path
        self.input_path = input_path
        self.p_path = p_path
        self.test_data = test_data

        if algorithm_name == "mcmc_domain":
            self.fitness = mcmc_fitness

        elif algorithm_name == "boundary_points":
            self.fitness = boundary_fitness

        elif algorithm_name == "multi_swarm_domain":
            self.fitness = multi_swarm_fitness

        elif algorithm_name == "speciation_domain":
            self.fitness = multi_swarm_fitness

        elif algorithm_name == "GA":
            self.fitness = multi_swarm_fitness

        elif algorithm_name == "GA_Local":
            self.fitness = multi_swarm_fitness

        global dims, instrumented_file, out_path, and_or_dict, pp_prime, trues_false, func, require, trace, boundary_delta, trues, falses, p_prime, p_requirement

        boundary_delta = _boundary_delta
        p_prime = p_path
        p_requirement = requirement
        func = function_name
        pp_prime = prime_pathes
        instrumented_file = function_name + "_instrumented"
        out_path = output_path + "/Code"
        with open(output_path + f"/Code/{instrumented_file}.py", 'r') as file:
            code = file.read()
        and_or_dict = and_or(code)
        trues_false = list(and_or_dict.keys())
        ar = get_argument_and_type(input_path, file_name, function_name)
        self.varbound, self.vartyp, self.arguments = dom_type(ar)
        dims = int(len(ar))

        trace_line = []
        trace = []
        trace_line = line_true_false(
            p_path, output_path)

        try:
            nums = pc_num_extract(source)
            for item in trace_line:
                trace.append((nums[item[0]][0], item[1]))
        except:
            pass

        print('trace_line: ', trace_line)
        print('trace: ', trace)

    def execute(self):
        if self.algorithm_name == "mcmc_domain":
            # path which try to generate domain p_prime
            # requirement for their path
            model = self.algorithm(function=self.fitness, vartype=self.vartyp, varbound=self.varbound,
                                   algorithm_parameters=self.algorithm_parameters)
            dom_point = model.run_dom_mcmc()
            return dom_point

        elif self.algorithm_name == "boundary_points":
            # extract csv file for test data
            model = self.algorithm(test_data=self.test_data, function=self.fitness, vartype=self.vartyp,
                                   varbound=self.varbound,
                                   p_prime=p_prime.copy(), algorithm_parameters=self.algorithm_parameters)
            datas = model.run_boundary_point()
            with open(f"{self.output_path}/Domain/boundary_{self.function_name}.csv", 'w', newline='') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(["boundary_datas"])
                for i in datas:
                    writer.writerow(i)

        elif self.algorithm_name == "GA":
            model = self.algorithm(function=self.fitness, vartype=self.vartyp, varbound=self.varbound,
                                   output_path=self.output_path, function_name=self.function_name)
            row = self.arguments + ['branch_distance', 'approach_level', 'fitness', 'label']
            with open(f'{self.output_path}/Domain/{self.function_name}_GA_domain.csv', 'w',
                      newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)
            dom_point = model.run_GA(10000)
            return dom_point

        elif self.algorithm_name == "GA_Local":
            model = self.algorithm(function=self.fitness, vartype=self.vartyp, varbound=self.varbound,
                                   output_path=self.output_path, function_name=self.function_name)
            row = self.arguments + ['branch_distance', 'approach_level', 'fitness', 'label']
            with open(f'{self.output_path}/Domain/{self.function_name}_GA_Local_domain.csv', 'w',
                      newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)
            dom_point = model.run_GA_local(500)
            return dom_point


        elif self.algorithm_name == "multi_swarm_domain":
            # path which try to generate domain p_prime
            # requirement for their path
            model = self.algorithm(function=self.fitness, vartype=self.vartyp, varbound=self.varbound,
                                   function_name=self.function_name,
                                   iteration=100, output_path=self.output_path)

            row = self.arguments + ['branch_distance', 'approach_level', 'fitness', 'label']
            with open(f'{self.output_path}/Domain/{self.function_name}_multi_swarm_domain.csv', 'w',
                      newline='') as file:  # append to sample_file
                writer = csv.writer(file)
                writer.writerow(row)

            dom_point = model.run_dom_multi_swarm()
            return dom_point
        elif self.algorithm_name == "speciation_domain":
            # path which try to generate domain p_prime
            # requirement for their path
            model = self.algorithm(function=self.fitness, vartype=self.vartyp, varbound=self.varbound,
                                   function_name=self.function_name,
                                   iteration=100, output_path=self.output_path)

            row = self.arguments + ['branch_distance', 'approach_level', 'fitness', 'label']
            with open(f'{self.output_path}/Domain/{self.function_name}_speciation_domain.csv', 'w',
                      newline='') as file:  # append to sample_file
                writer = csv.writer(file)
                writer.writerow(row)

            dom_point = model.run_dom_multi_swarm()
            return dom_point


def update_maps(condition_num, d_true, d_false):
    global clause_distances_true, clause_distances_false

    print('current condition num -->', condition_num)
    print(d_true)
    clause_distances_true.append(d_true)

    print(d_false)
    clause_distances_false.append(d_false)


def evaluate_condition(num, op, lhs, rhs):
    distance_true = 0
    distance_false = 0
    result = False
    K = 0.0001

    if isinstance(lhs, str):
        lhs = ord(lhs)
    if isinstance(rhs, str):
        rhs = ord(rhs)

    if op == "Eq":
        if lhs == rhs:
            distance_false = K
        else:
            distance_true = abs(lhs - rhs)

    elif op == "NotEq":
        if lhs != rhs:
            distance_false = abs(lhs - rhs)
        else:
            distance_true = K

    elif op == "Lt":
        if lhs < rhs:
            distance_false = rhs - lhs
        else:
            distance_true = lhs - rhs + K

    elif op == "LtE":
        if lhs <= rhs:
            distance_false = rhs - lhs + K
            print('****************', distance_false)
        else:
            distance_true = lhs - rhs

    elif op == "Gt":
        if lhs > rhs:
            distance_false = lhs - rhs
        else:
            distance_true = rhs - lhs + K

    elif op == "GtE":
        if lhs >= rhs:
            distance_false = lhs - rhs + K
            print('****************', distance_false)
        else:
            distance_true = rhs - lhs
            print('****************', distance_true)

    elif op == "In":
        minimum = sys.maxsize
        for elem in rhs:
            distance = abs(lhs - elem)
            if distance < minimum:
                minimum = distance

        distance_true = minimum
        if distance_true == 0:
            distance_false = K
            # result = True

    update_maps(num, distance_true, distance_false)

    if distance_true == 0:
        return True
    else:
        return False


def check(l1, l2):
    # return True if list2 is sublist of list1 but order of l2 is same in l1.
    index_list = [i for i, v in enumerate(l1) if v == l2[0]]
    for ii in index_list:
        l1_slice = l1[ii:ii + len(l2)]
        if l1_slice == l2:
            return True
    else:
        return False


def normalize(x):
    return x / (1.0 + x)


def get_fitness():
    pass


def multi_swarm_fitness(x):
    print("x:", x)

    exe_file = instrumented_file
    sys.path.append(out_path)
    exec(f"from {instrumented_file} import {instrumented_file}")
    argss = ""
    for i in range(0, dims):
        argss += f"x[{str(i)}],"
    exe_file += "(" + argss[:-1] + ")"
    executed_path, result = eval(exe_file)

    listOfGlobals = globals()
    boundary_delta = listOfGlobals['boundary_delta']
    branch_distance, approach_level, fitness, label = calculate_boundary_distance(boundary_delta, trace)

    return branch_distance, approach_level, fitness, label


from collections import deque


def parse(tokens, result=True):
    if not result:
        return result
    token = tokens.popleft()
    if token == 'And':
        return parse(tokens) and parse(tokens)
    elif token == 'Or':
        return parse(tokens) or parse(tokens)
    else:
        return evaluate_condition(*token)


def parse_branch_distance(condition_set, tokens, clause_distances_true, clause_distances_false, result=True):
    if not result:
        return result, clause_distances_true, clause_distances_false

    token = tokens.popleft()
    if token == 'And':
        lhs_condition, result, lhs_distance_true, lhs_distance_false = parse_branch_distance(condition_set, tokens,
                                                                                             clause_distances_true,
                                                                                             clause_distances_false,
                                                                                             result)
        if len(clause_distances_true) < 1 or len(clause_distances_false) < 1:
            distance_true = lhs_distance_true
            distance_false = lhs_distance_false
            condition = lhs_condition
            result = False
        else:
            rhs_condition, result, rhs_distance_true, rhs_distance_false = parse_branch_distance(condition_set, tokens,
                                                                                                 clause_distances_true,
                                                                                                 clause_distances_false,
                                                                                                 result)
            distance_true = max([lhs_distance_true, rhs_distance_true])
            distance_false = max([lhs_distance_false, rhs_distance_false])
            condition = lhs_condition and rhs_condition
            result = lhs_distance_true == rhs_distance_true == 0

        print('-----> distance_true: ', distance_true)
        print('-----> distance_false: ', distance_false)
        clause_distances_true.extendleft([distance_true])
        clause_distances_false.extendleft([distance_false])
        condition_set.extendleft([condition])
    elif token == 'Or':
        lhs_condition, result, lhs_distance_true, lhs_distance_false = parse_branch_distance(condition_set, tokens,
                                                                                             clause_distances_true,
                                                                                             clause_distances_false,
                                                                                             result)
        if len(clause_distances_true) < 1 or len(clause_distances_false) < 1:
            distance_true = lhs_distance_true
            distance_false = lhs_distance_false
            condition = lhs_condition
            result = lhs_distance_true == 0
        else:
            rhs_condition, result, rhs_distance_true, rhs_distance_false = parse_branch_distance(condition_set, tokens,
                                                                                                 clause_distances_true,
                                                                                                 clause_distances_false,
                                                                                                 result)
            distance_true = min([lhs_distance_true, rhs_distance_true])
            distance_false = min([lhs_distance_false, rhs_distance_false])
            condition = lhs_condition or rhs_condition
            result = lhs_distance_true == 0 or rhs_distance_true == 0

        print('-----> distance_true: ', distance_true)
        print('-----> distance_false: ', distance_false)
        clause_distances_true.extendleft([distance_true])
        clause_distances_false.extendleft([distance_false])
        condition_set.extendleft([condition])

    clause_distances_true_popleft = clause_distances_true.popleft()
    clause_distances_false_popleft = clause_distances_false.popleft()
    condition_set_popleft = condition_set.popleft()

    print('-----> clause_distances_true_popleft: ', clause_distances_true_popleft)
    print('-----> clause_distances_false_popleft: ', clause_distances_false_popleft)
    print('-----> condition_set_popleft: ', condition_set_popleft)
    print('******')

    if clause_distances_true_popleft == 0:
        if condition_set_popleft:
            clause_distances_false_popleft = -clause_distances_false_popleft
    else:
        if not condition_set_popleft:
            clause_distances_true_popleft = -clause_distances_true_popleft

    return condition_set_popleft, result, clause_distances_true_popleft, clause_distances_false_popleft


def convert_to_inorder(tokens):
    token = tokens.popleft()
    if token == 'And':
        return '({} and {})'.format(convert_to_inorder(tokens), convert_to_inorder(tokens))
    elif token == 'Or':
        return '({} or {})'.format(convert_to_inorder(tokens), convert_to_inorder(tokens))
    else:
        return token


import truths


def generate_truth_table(args, expression, oracle):
    result = []
    truths_table = truths.Truths(args, ints=False)
    for conditions_set in truths_table.base_conditions:
        g = Gob()
        for a, b in zip(truths_table.base, conditions_set):
            setattr(g, a, b)

        item = truths_table.p.sub(r'g.\1', expression)
        eval_phrase = eval(item)
        if eval_phrase == oracle:
            result.append(conditions_set)

    return result


def evaluate_branch_distance(*args):
    print('current branch num ------------> ', args)
    branch_num = args[0]
    args = args[1:]

    listOfGlobals = globals()
    branch_distances_true = listOfGlobals['branch_distances_true']
    trace = listOfGlobals['trace']
    listOfGlobals['clause_distances_true'] = []
    listOfGlobals['clause_distances_false'] = []

    # calculate clause distance
    branch_result = parse(deque(args))

    idx = len(branch_distances_true)
    if trace[idx][0] != branch_num:
        branch_num = -1
        branch_distance_true = None
        branch_distance_false = None
    else:
        # clculate branch distance
        clause_distances_true = listOfGlobals['clause_distances_true']
        clause_distances_false = listOfGlobals['clause_distances_false']
        print('clause_distances_true: ', clause_distances_true)
        print('clause_distances_false: ', clause_distances_false)

        expression = []
        operand_num = 0
        for item in args:
            if item in ['And', 'Or']:
                expression.append(item)
            else:
                expression.append('x{}'.format(item[0]))
                operand_num += 1

        expression = convert_to_inorder(deque(expression))
        arguments = ['x{}'.format(i + 1) for i in range(operand_num)]
        condition_sets = generate_truth_table(arguments, expression, trace[idx][1] == 'T')

        idx = len(clause_distances_true)
        eval_branch = []
        for condition_set in condition_sets:
            print('condition_set --->', condition_set)
            _, _, branch_distance_true, branch_distance_false = parse_branch_distance(
                deque(copy.copy(condition_set[0:idx])), deque(args), deque(copy.copy(clause_distances_true)),
                deque(copy.copy(clause_distances_false)))
            eval_branch.append([branch_distance_true, branch_distance_false])

        print('eval_branch.................>', eval_branch)
        branch_distance_true = min(eval_branch, key=lambda items: item[0])[0]
        branch_distance_false = min(eval_branch, key=lambda items: item[1])[1]

        if branch_result:
            branch_distance_true = 0
        else:
            branch_distance_false = 0
        # else:

    branch_distances_true.append([branch_num, branch_distance_true])
    listOfGlobals['branch_distances_true'] = branch_distances_true
    branch_distances_false.append([branch_num, branch_distance_false])
    listOfGlobals['branch_distances_false'] = branch_distances_false

    return branch_result


def calculate_boundary_distance(boundary_delta, trace):
    listOfGlobals = globals()
    branch_distances_true = listOfGlobals['branch_distances_true']
    branch_distances_false = listOfGlobals['branch_distances_false']

    traversed_path = [item[0] for item in branch_distances_true]
    print('traversed_path: ', branch_distances_true)
    approach_level = 0
    branch_distance = 0
    branch_distances = []

    for idx, predicate in enumerate(trace):
        print('idx: {}, predicate: {}', idx, predicate)
        if len(traversed_path) - 1 < idx or predicate[0] != traversed_path[idx]:
            approach_level += len(trace) - idx
            break
        else:
            if predicate[1] == 'T':
                if branch_distances_true[idx][1] == 0:
                    branch_distance = branch_distances_false[idx][1]
                else:
                    branch_distance = branch_distances_true[idx][1]
            elif predicate[1] == 'F':
                if branch_distances_true[idx][1] == 0:
                    branch_distance = branch_distances_false[idx][1]
                else:
                    branch_distance = branch_distances_true[idx][1]
            branch_distances.append(branch_distance)

    print('current branch_distances: ', branch_distances)
    mbd = np.max(branch_distances)

    h_branch_distance = math.fabs(mbd)
    if mbd <= 0 and approach_level == 0:
        label = 1  # feasible
        if h_branch_distance <= boundary_delta:
            h_branch_distance = 0
    else:
        label = 0

    branch_distance = normalize(h_branch_distance)

    print("distances_true: ", branch_distances_true)
    print("distances_false: ", branch_distances_false)
    print("branch_distance: ", branch_distance)
    print('approach_level: ', approach_level)

    fitness = approach_level + branch_distance
    print('fitness: ', fitness)
    print('...................................')

    listOfGlobals['branch_distances_true'] = []
    listOfGlobals['branch_distances_false'] = []

    print('initial  branch_distances_true ->', listOfGlobals['branch_distances_true'])
    print('initial  branch_distances_false ->', listOfGlobals['branch_distances_false'])

    return branch_distance, approach_level, fitness, label


def boundary_fitness(x):
    directori = os.path.dirname(os.path.realpath(__file__))

    exe_file = instrumented_file
    sys.path.append(out_path)
    exec(f"from {instrumented_file} import {instrumented_file}")
    argss = ""
    for i in range(0, dims):
        argss += f"x[{str(i)}],"
    exe_file += "(" + argss[:-1] + ")"
    executed_path, result = eval(exe_file)
    dir1 = directori + '/Trues'
    distances_true = pickle.load(open(dir1, "rb"))
    print(distances_true)
    NC = 0
    covered_list = list()
    for i in p_requirement:
        if check(executed_path, i) is True:
            covered_list.append(i)
            NC += 1
    # Sum up branch distances
    fitness = 0.0
    for branch in trues_false:
        if branch in distances_true:
            if and_or_dict[branch] == "and":
                fitness += normalize(distances_true[branch])
            elif and_or_dict[branch] == "or":
                fitness = min(fitness, normalize(distances_true[branch]))
    return fitness
