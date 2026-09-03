import ast
import os
import astor
from collections import defaultdict

import astunparse

line_cond = defaultdict(list)
line_cond_num = defaultdict(list)
imports = list()


class BranchTransformer(ast.NodeTransformer):
    branch_num = 0
    clause_num = 0
    pre_order_expression = []

    def visit_FunctionDef(self, node):
        node.name = node.name + "_instrumented"
        return self.generic_visit(node)

    def visit_Clause(self, node):
        # line_cond[node.lineno].append(astor.to_source(node))

        if node.ops[0] in [ast.Is, ast.IsNot, ast.In, ast.NotIn]:
            return node

        # self.branch_num += 1
        # line_cond_num[node.lineno].append(self.branch_num)
        # line_cond_num[node.lineno].append(branch_num)

        # return ast.Call(func=ast.Name("evaluate_condition", ast.Load()),
        #                 args=[ast.Num(self.branch_num), ast.Str(node.ops[0].__class__.__name__), node.left,
        #                       node.comparators[0]], keywords=[], starargs=None, kwargs=None)

        # args = [self.branch_num, ast.Str(node.ops[0].__class__.__name__), ast.Str(node.left),
        #         ast.Str(node.comparators[0])]
        # return ast.Str("evaluate_condition({}, {}, {}, {})".format(*args))

        # function_call = str.strip(astunparse.unparse(ast.Call(func=ast.Name("evaluate_condition", ast.Load()),
        #   args=[ast.Str(node.ops[0].__class__.__name__), node.left,
        #   node.comparators[0]], keywords=[], starargs=None, kwargs=None)))
        # return ast.Str(function_call)

        # line_cond[node.lineno].append(astor.to_source(node))
        self.clause_num += 1
        # line_cond_num[node.lineno].append(self.clause_num)

        return ast.List(elts=[ast.Num(self.clause_num), ast.Str(node.ops[0].__class__.__name__), node.left,
                              node.comparators[0]], ctx=ast.Store())

    def visit_If(self, node):
        self.clause_num = 0
        node.test = self.visit_branch(node)
        return self.generic_visit(node)

    def visit_While(self, node):
        self.clause_num = 0
        node.test = self.visit_branch(node)
        return self.generic_visit(node)

    def visit_branch(self, node):
        line_cond[node.lineno].append(astor.to_source(node))
        self.branch_num += 1
        line_cond_num[node.lineno].append(self.branch_num)
        global pre_order_expression
        pre_order_expression = []
        self.visit_BoolianOp(node.test)
        return ast.Call(func=ast.Name("evaluate_branch_distance", ast.Load()),
                        args=[ast.Num(self.branch_num), *pre_order_expression], keywords=[], starargs=None, kwargs=None)

    def visit_BoolianOp(self, node):
        if isinstance(node, ast.Compare):
            instrumented_cluase = self.visit_Clause(node)
            pre_order_expression.append(instrumented_cluase)
            return
        cluases = node.values

        compare_clause = 0
        for cluase in cluases:
            if isinstance(cluase, ast.Compare):
                compare_clause += 1

        pre_order_expression.append(ast.Str(node.op.__class__.__name__))

        for cluase in cluases:
            if isinstance(cluase, ast.Compare):
                instrumented_cluase = self.visit_Clause(cluase)
                pre_order_expression.append(instrumented_cluase)
                if compare_clause > 2:
                    pre_order_expression.append(ast.Str(node.op.__class__.__name__))
                    compare_clause -= 1
            elif isinstance(cluase, ast.BoolOp):
                self.visit_BoolianOp(cluase)

        # pre_order_traversal = []
        # cond = node.test
        # expr = ast.Expression(cond)
        # if isinstance(expr.body, ast.BoolOp):
        #     pre_order_traversal.append(expr.body.op.__class__.__name__)
        #
        # for v in expr.body.values:
        #     if isinstance(v, ast.Name):
        #         pre_order_traversal.append(v.id)
        #     else:
        #         self.visit_BoolOp(v)

        # instrumented_cluses = []
        # for cluase in node:
        #     instrumented_cluase, branch_num = self.visit_Cluase(cluase)
        #     instrumented_cluses.append(instrumented_cluase)


def save_as_instrumented_python(instrumented, input_file, name, path):
    out_path = path + "/Code/" + f"{name}_instrumented.py"
    evalue_dir = os.path.dirname(os.path.abspath(__file__))
    cov_dir = evalue_dir[:-11]
    imports = import_count(path + "/Code", input_file)
    extra = max_line(path, input_file, name)

    with open(out_path, "w") as file:
        for i in imports:
            file.write(i)
        file.write("import sys\n")
        file.write("sys.path.append(r'{a}')\n".format(a=evalue_dir))
        file.write("sys.path.append(r'{a}')\n".format(a=cov_dir))
        # file.write("from runner import evaluate_condition\n")
        file.write("from src.runner import evaluate_branch_distance\n")
        file.write("from Coverage import cover_decorator\n")  # fix problem
        file.write("\n")
        file.write("@cover_decorator\n")
        ins = instrumented.replace("True", "True is True")
        file.write(f"{ins}")
        for i in extra:
            file.write(i)


def max_line(input_path, file, func):
    ffile = open(input_path + "/Code/" + file + ".py", "r")
    lines = ffile.readlines()
    rang = len(lines)
    name = "def " + str(func)
    min_number = float("inf")
    for number, line in enumerate(lines):
        if name in line:
            min_number = number + 1
        elif ("def" in line and number > min_number - 1):
            max_number = number
            break
        elif number == rang - 1:
            max_number = number + 1
        else:
            continue
    extra = lines[max_number:]
    return extra


def instrument_extraction(source, input_file, func_name, path):
    node = ast.parse(source)
    BranchTransformer().visit(node)
    node = ast.fix_missing_locations(node)
    save_as_instrumented_python(astor.to_source(node), input_file, func_name, path)


def conditions(source):
    global line_cond
    global line_cond_num
    line_cond = defaultdict(list)
    line_cond_num = defaultdict(list)
    node = ast.parse(source)
    BranchTransformer().visit(node)
    node = ast.fix_missing_locations(node)
    return line_cond, line_cond_num


def import_count(path, mod):
    imports = list()
    count = 0
    tree = ast.parse(open(f'{path}/{mod}.py').read())
    for i in ast.walk(tree):
        if i.__class__.__name__ == "Import":
            imports.append(astor.to_source(i))
            count += 1
    return imports
