#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

"""Implementation of the Multiswarm Particle Swarm Optimization algorithm as
presented in *Blackwell, Branke, and Li, 2008, Particzle Swarms for Dynamic
Optimization Problems.*
"""
import copy
import csv
import itertools
import math
import operator
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy
import numpy as np

from domain.multi_swarm.incremental_svclustering import isvc
from domain.multi_swarm.local_search import hill_climbing, local_search

try:
    from itertools import imap
except:
    # Python 3 nothing to do
    pass
else:
    map = imap

from deap import base
from deap.benchmarks import movingpeaks
from deap import creator
from deap import tools


class MultiSwarmDom:
    def __init__(self, function, vartype, varbound, output_path, iteration, function_name,
                 algorithm_parameters={'test_budget': None,
                                       'max_chanin_long': 30,
                                       'agent_number': 10,
                                       'step_size': 2}):
        # data must be compatible with type of int and float
        self.iteration = iteration
        self.dimension = len(vartype)
        self.vartype = vartype
        self.varbound = varbound
        self.answer_list = list()

        self.min_coord = varbound[0][0]
        self.max_coord = varbound[0][1]
        self.fitness_function = function
        self.figs_path = f'{output_path}/Domain'
        self.sample_path = f'{output_path}/Domain/{function_name}_multi_swarm_domain.csv'
        self.verbose = True
        self.output_path = output_path
        self.delta = 0.5
        self.N = 20

    def generate(self, pclass, dim, pmin, pmax, smin, smax):
        part = pclass(random.uniform(pmin, pmax) for _ in range(dim))
        part.speed = [random.uniform(smin, smax) for _ in range(dim)]
        return part

    def convertQuantum(self, swarm, rcloud, centre, dist):
        dim = len(swarm[0])
        for part in swarm:
            position = [random.gauss(0, 1) for _ in range(dim)]
            dist = math.sqrt(sum(x ** 2 for x in position))

            if dist == "gaussian":
                u = abs(random.gauss(0, 1.0 / 3.0))
                part[:] = [(rcloud * x * u ** (1.0 / dim) / dist) + c for x, c in zip(position, centre)]

            elif dist == "uvd":
                u = random.random()
                part[:] = [(rcloud * x * u ** (1.0 / dim) / dist) + c for x, c in zip(position, centre)]

            elif dist == "nuvd":
                u = abs(random.gauss(0, 1.0 / 3.0))
                part[:] = [(rcloud * x * u / dist) + c for x, c in zip(position, centre)]

            del part.fitness.values
            del part.bestfit.values
            part.best = None

        return swarm

    def updateParticle(self, part, best, chi, c):
        ce1 = (c * random.uniform(0, 1) for _ in range(len(part)))
        ce2 = (c * random.uniform(0, 1) for _ in range(len(part)))
        ce1_p = map(operator.mul, ce1, map(operator.sub, best, part))
        ce2_g = map(operator.mul, ce2, map(operator.sub, part.best, part))
        a = map(operator.sub,
                map(operator.mul,
                    itertools.repeat(chi),
                    map(operator.add, ce1_p, ce2_g)),
                map(operator.mul,
                    itertools.repeat(1 - chi),
                    part.speed))
        part.speed = list(map(operator.add, part.speed, a))
        part[:] = list(map(operator.add, part, part.speed))

    def plotting(self, data_set, figs_path, generation):
        ds = data_set.loc[(data_set['fitness'] == 0)]
        # ds = data_set
        if len(ds) == 0:
            return
        if self.dimension == 2:
            print('.............plotting: {}...........................'.format(
                ds.groupby(['x', 'y'], as_index=False).count()))
            plt.scatter(ds.iloc[:, 0].to_list(), ds.iloc[:, 1].to_list(), s=5)
            # pts = np.array([[-4.053836582, -2.827101845], [3.542466494, -3.816595838], [-2.420214529, -3.036474555],
            #                 [-0.09342022, -3.339746182]])
            # pts = np.array([[-2.420214529, -3.036474555]])
            # plt.scatter(pts[:, 0], pts[:, 1], marker="x", color="red", s=5)
            plt.xlabel('x')
            plt.ylabel('y')

            plt.savefig('{}/domain-generation-{}.png'.format(figs_path, generation))
            # plt.show()
            # plt.close()
        elif self.dimension == 3:
            print('.............plotting: {}...........................'.format(
                ds.groupby(['x', 'y', 'z'], as_index=False).count()))
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(ds.iloc[:, 0].to_list(), ds.iloc[:, 1].to_list(), ds.iloc[:, 2].to_list(), marker='o')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.view_init(30, 30)
            plt.savefig('{}/domain-generation-{}.png'.format(figs_path, generation))
            # plt.show()

    def evaluate_function(self, part, verbose=True):
        for i in range(self.dimension):
            if not (self.min_coord <= part[i] <= self.max_coord):
                part[i] = random.uniform(self.min_coord, self.max_coord)

        branch_distance, approach_level, fitness, label = self.fitness_function(part)
        with open(self.sample_path, 'a', newline='') as file:  # append to sample_file
            writer = csv.writer(file)
            writer.writerow([*part, branch_distance, approach_level, fitness, label])
        # return values[-2], #fitness
        if verbose:
            return ((fitness,)), label
        return fitness,

    def run_dom_multi_swarm(self):
        NDIM = self.dimension
        BOUNDS = [self.min_coord, self.max_coord]

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Particle", list, fitness=creator.FitnessMin, speed=list,
                       best=None, bestfit=creator.FitnessMin, statues=0)
        creator.create("Swarm", list, best=None, bestfit=creator.FitnessMin)

        toolbox = base.Toolbox()
        toolbox.register("particle", self.generate, creator.Particle, dim=NDIM,
                         pmin=BOUNDS[0], pmax=BOUNDS[1], smin=-(BOUNDS[1] - BOUNDS[0]) / 2.0,
                         smax=(BOUNDS[1] - BOUNDS[0]) / 2.0)
        toolbox.register("swarm", tools.initRepeat, creator.Swarm, toolbox.particle)
        toolbox.register("update", self.updateParticle, chi=0.729843788, c=2.05)
        toolbox.register("convert", self.convertQuantum, dist="nuvd")
        toolbox.register("evaluate", self.evaluate_function)

        NSWARMS = 1
        NPARTICLES = 5
        NEXCESS = 3
        RCLOUD = 0.5  # 0.5 times the move severity

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        logbook = tools.Logbook()
        logbook.header = "gen", "nswarm", "evals", "avg", "min"

        # Generate the initial population
        population = [toolbox.swarm(n=NPARTICLES) for _ in range(NSWARMS)]

        # Evaluate each particle
        for swarm in population:
            for part in swarm:
                part.fitness.values, part.statues = toolbox.evaluate(part)

                # Update swarm's attractors personal best and global best
                if not part.best or part.fitness > part.bestfit:
                    part.best = toolbox.clone(part[:])  # Get the position
                    part.bestfit.values = part.fitness.values  # Get the fitness
                if not swarm.best or part.fitness > swarm.bestfit:
                    swarm.best = toolbox.clone(part[:])  # Get the position
                    swarm.bestfit.values = part.fitness.values  # Get the fitness

        record = stats.compile(itertools.chain(*population))
        logbook.record(gen=0, evals=self.iteration, nswarm=len(population),
                       **record)

        if self.verbose:
            print(logbook.stream)

        generation = 1
        while self.iteration < 5e5:
            # Check for convergence
            rexcl = (BOUNDS[1] - BOUNDS[0]) / (2 * len(population) ** (1.0 / NDIM))

            not_converged = 0
            worst_swarm_idx = None
            worst_swarm = None
            for i, swarm in enumerate(population):
                # Compute the diameter of the swarm
                for p1, p2 in itertools.combinations(swarm, 2):
                    d = math.sqrt(sum((x1 - x2) ** 2. for x1, x2 in zip(p1, p2)))
                    if d > 2 * rexcl:
                        not_converged += 1
                        # Search for the worst swarm according to its global best
                        if not worst_swarm or swarm.bestfit < worst_swarm.bestfit:
                            worst_swarm_idx = i
                            worst_swarm = swarm
                        break

            # If all swarms have converged, add a swarm
            if not_converged == 0:
                population.append(toolbox.swarm(n=NPARTICLES))
            # If too many swarms are roaming, remove the worst swarm
            elif not_converged > NEXCESS:
                population.pop(worst_swarm_idx)

            # Update and evaluate the swarm
            for swarm in population:
                # Check for change
                if swarm.best and toolbox.evaluate(swarm.best, verbose=False) != swarm.bestfit.values:
                    # Convert particles to quantum particles
                    swarm[:] = toolbox.convert(swarm, rcloud=RCLOUD, centre=swarm.best)
                    swarm.best = None
                    del swarm.bestfit.values

                for part in swarm:
                    # Not necessary to update if it is a new swarm
                    # or a swarm just converted to quantum
                    if swarm.best and part.best:
                        toolbox.update(part, swarm.best)
                    part.fitness.values, part.statues = toolbox.evaluate(part)

                    # Update swarm's attractors personal best and global best
                    if not part.best or part.fitness > part.bestfit:
                        part.best = toolbox.clone(part[:])
                        part.bestfit.values = part.fitness.values
                    if not swarm.best or part.fitness > swarm.bestfit:
                        swarm.best = toolbox.clone(part[:])
                        swarm.bestfit.values = part.fitness.values

            record = stats.compile(itertools.chain(*population))
            logbook.record(gen=generation, evals=self.iteration, nswarm=len(population),
                           **record)

            if self.verbose:
                print('\n\n######################################\n')
                print(logbook.stream)
                print('\n######################################\n\n')
                test_suite = pd.read_csv(self.sample_path)
                self.plotting(test_suite, self.figs_path, generation)

            # Apply exclusion
            reinit_swarms = set()
            for s1, s2 in itertools.combinations(range(len(population)), 2):
                # Swarms must have a best and not already be set to reinitialize
                if population[s1].best and population[s2].best and not (s1 in reinit_swarms or s2 in reinit_swarms):
                    dist = 0
                    for x1, x2 in zip(population[s1].best, population[s2].best):
                        dist += (x1 - x2) ** 2.
                    dist = math.sqrt(dist)
                    if dist < rexcl:
                        if population[s1].bestfit <= population[s2].bestfit:
                            reinit_swarms.add(s1)
                        else:
                            reinit_swarms.add(s2)

            # Reinitialize and evaluate swarms
            # if len(reinit_swarms) > 0:
            # print('-------------------------------------------------isvc: #',len(reinit_swarms))
            # data_set = pd.read_csv(self.sample_path)
            # data_set = data_set.loc[(data_set['fitness'] == 0)]
            # if len(data_set) > 10:
            #     ms = data_set.to_numpy()
            #     clusters = isvc(ms)
            #     print(clusters)

            for s in reinit_swarms:
                # approach1
                # data_set = pd.read_csv(self.sample_path)
                # # data_set = data_set.loc[(data_set['fitness'] == 0)]
                # if len(data_set) > 100:
                #     ms = data_set.to_numpy()
                #     sv_0, sv_1 = isvc(ms)
                #     support_vectors = []
                #     support_vectors.extend(sv_0)
                #     support_vectors.extend(sv_1)
                #
                #     if len(support_vectors) >= NPARTICLES:
                #         population[s][0:NPARTICLES] = copy.copy(support_vectors[0:NPARTICLES])
                #     else:
                #         population[s][0:len(support_vectors)] = copy.copy(support_vectors)
                #         size = len(support_vectors)
                #         nparticles = NPARTICLES - size
                #         population[s][size:NPARTICLES] = toolbox.swarm(n=nparticles)

                # approach2
                # population[s] = toolbox.swarm(n=NPARTICLES)
                # data_set = pd.read_csv(self.sample_path)
                # data_set = data_set.loc[(data_set['fitness'] == 0)]
                # nparticles = random.randrange(NPARTICLES) + 1
                # idxs = []
                # if nparticles <= len(data_set):
                #     print('*********************************************************************reinit')
                #     idxs = random.sample(range(len(data_set)), nparticles)
                #     for i, item in enumerate(idxs):
                #         new_part = data_set.values[item][0:self.dimension].tolist()
                #         population[s][i][:] = toolbox.clone(new_part)
                #
                # for i, part in enumerate(population[s]):
                #     if i not in idxs:
                #         part.fitness.values = toolbox.evaluate(part)
                #     else:
                #         part.fitness.values = 0,
                #
                #     # Update swarm's attractors personal best and global best
                #     if not part.best or part.fitness > part.bestfit:
                #         part.best = toolbox.clone(part[:])
                #         part.bestfit.values = part.fitness.values
                #     if not population[s].best or part.fitness > population[s].bestfit:
                #         population[s].best = toolbox.clone(part[:])
                #         population[s].bestfit.values = part.fitness.values

                # approach3
                population[s] = toolbox.swarm(n=NPARTICLES)
                for part in population[s]:
                    part.fitness.values, part.statues = toolbox.evaluate(part)
                    # Update swarm's attractors personal best and global best
                    if not part.best or part.fitness > part.bestfit:
                        part.best = toolbox.clone(part[:])
                        part.bestfit.values = part.fitness.values
                    if not population[s].best or part.fitness > population[s].bestfit:
                        population[s].best = toolbox.clone(part[:])
                        population[s].bestfit.values = part.fitness.values

            # local search
            print('-------------------------------------------------local search:')
            # appraoch1:
            # for i, s in enumerate(population):
            #     for j, part in enumerate(s):
            #         if len(part.fitness.values) > 0 and part.fitness.values[0] == 0:
            #             new_part = self.hill_climbing(toolbox.clone(part[:]),
            #                                      toolbox.clone(part.fitness.values[0]), self.delta, self.N)
            #             population[i][j][:] = toolbox.clone(new_part)
            #             population[i][j].best = toolbox.clone(new_part[:])

            # approach2:
            # for i, s in enumerate(population):
            #     for part in s:
            #         new_part, fitness = hill_climbing(toolbox.clone(part[:]),
            #                                  toolbox.clone(part.fitness.values[0]), self.delta, self.N, self.evaluate_function)
            #         fitness_min = toolbox.clone(part.fitness)
            #         fitness_min.values = fitness
            #         # Update swarm's attractors personal best and global best
            #         if not part.best or fitness_min > part.bestfit:
            #             part.best = toolbox.clone(new_part[:])
            #             part.bestfit.values = fitness_min.values
            #         if not population[i].best or fitness_min > population[i].bestfit:
            #             population[i].best = toolbox.clone(new_part[:])
            #             population[i].bestfit.values = fitness_min.values

            # approach3:
            # for i, s in enumerate(population):
            #     for j, part in enumerate(s):
            #         if len(part.fitness.values) > 0 and part.fitness.values[0] == 0:
            #             new_part = self.boundary_identifier(toolbox.clone(part[:]),
            #                                      toolbox.clone(part.fitness.values[0]), self.delta, self.N)
            #             population[i][j][:] = toolbox.clone(new_part)
            #             population[i][j].best = toolbox.clone(new_part[:])

            # approach4:
            # for i, s in enumerate(population):
            #     for j, part in enumerate(s):
            #         if len(part.fitness.values) > 0 and part.fitness.values[0] == 0:
            #             new_part = self.local_search(toolbox.clone(part[:]),
            #                                      toolbox.clone(part.fitness.values[0]), self.delta, self.N)
            #             population[i][j][:] = toolbox.clone(new_part)
            #             population[i][j].best = toolbox.clone(new_part[:])

            # approach5:
            for i, s in enumerate(population):
                for j, part in enumerate(s):
                    if len(part.fitness.values) > 0 and part.statues == 1:  # and part.fitness.values[0] != 0:
                        new_part, fitness, label = local_search(toolbox.clone(part[:]),
                                                                toolbox.clone(part.fitness.values[0]), part.statues,
                                                                self.delta, self.N,
                                                                self.evaluate_function)
                        fitness_min = toolbox.clone(part.fitness)
                        fitness_min.values = fitness
                        # Update swarm's attractors personal best and global best
                        if not part.best or fitness_min > part.bestfit:
                            part.best = toolbox.clone(new_part[:])
                            part.bestfit.values = fitness_min.values
                            part.statues = label
                        if not population[i].best or fitness_min > population[i].bestfit:
                            population[i].best = toolbox.clone(new_part[:])
                            population[i].bestfit.values = fitness_min.values

            # approach6:
            # for i, s in enumerate(population):
            #     for j, part in enumerate(s):
            #         new_part = self.hill_climbing_v1(toolbox.clone(part[:]),
            #                                       toolbox.clone(part.fitness.values[0]), self.delta, self.N)
            #         population[i][j][:] = toolbox.clone(new_part)
            #         population[i][j].best = toolbox.clone(new_part[:])

            # # approach7:
            # data_set = pd.read_csv(self.sample_path)
            # data_set = data_set.loc[(data_set['fitness'] == 0)]
            # for row in data_set.values:
            #     record = row.tolist()
            #     new_part = hill_climbing(record[0:self.dimension],
            #                              record[-1], self.delta, self.N, self.fitness_function)

            generation += 1
