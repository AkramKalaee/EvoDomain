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

"""Implementation of the Speciation Particle Swarm Optimization algorithm as
presented in *Li, Blackwell, and Branke, 2006, Particle Swarm with Speciation
and Adaptation in a Dynamic Environment.*
"""
import csv
import itertools
import math
import operator
import random

import numpy

from domain.multi_swarm import local_search

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
import matplotlib.pyplot as plt
import pandas as pd


class SpeciationDom:
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
        self.max_coord =  varbound[0][1]
        self.fitness_function = function
        self.figs_path= f'{output_path}/Domain'
        self.sample_path = f'{output_path}/Domain/{function_name}_speciation_domain.csv'
        self.verbose = True
        self.output_path = output_path
        self.delta = 0.5
        self.N = 20

    def generate(self, pclass, dim, pmin, pmax, smin, smax):
        part = pclass(random.uniform(pmin, pmax) for _ in range(dim))
        part.speed = [random.uniform(smin, smax) for _ in range(dim)]
        return part


    def convert_quantum(self, swarm, rcloud, centre):
        dim = len(swarm[0])
        for part in swarm:
            position = [random.gauss(0, 1) for _ in range(dim)]
            dist = math.sqrt(sum(x ** 2 for x in position))
            choice = 1 #random.choice(range(3))
            if choice == 0:
                # Gaussian distribution
                u = abs(random.gauss(0, 1.0/3.0))
                part[:] = [(rcloud * x * u**(1.0/dim) / dist) + c for x, c in zip(position, centre)]
            elif choice == 1:
                # UVD distribution
                u = random.random()
                part[:] = [(rcloud * x * u**(1.0/dim) / dist) + c for x, c in zip(position, centre)]
            else:
                # NUVD distribution
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
        if len(ds) == 0:
            return
        if self.dimension == 2:
            print('.............plotting: {}...........................'.format(
                ds.groupby(['x', 'y'], as_index=False).count()))
            plt.scatter(ds.iloc[:, 0].to_list(), ds.iloc[:, 1].to_list(), s=5)
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

    def evaluate_function(self, part):
        for i in range(self.dimension):
            if not(self.min_coord <= part[i] <= self.max_coord):
                part[i] = random.uniform(self.min_coord, self.max_coord)

        branch_distance, approach_level, fitness, label = self.fitness_function(part)
        with open(self.sample_path, 'a', newline='') as file:  # append to sample_file
            writer = csv.writer(file)
            writer.writerow([*part, branch_distance, approach_level, fitness, label])
        # return values[-2], #fitness
        return fitness,

    def run_dom_multi_swarm(self):
        # scenario = movingpeaks.SCENARIO_2

        NDIM = self.dimension
        BOUNDS = [self.min_coord, self.max_coord]

        # mpb = problem

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
        toolbox.register("convert", self.convert_quantum, dist="nuvd")
        toolbox.register("evaluate", self.evaluate_function)


        NPARTICLES = 100
        RS = (BOUNDS[1] - BOUNDS[0]) / (50 ** (1.0 / NDIM))  # between 1/20 and 1/10 of the domain's range
        PMAX = 10
        RCLOUD = 1.0  # 0.5 times the move severity

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        logbook = tools.Logbook()
        logbook.header = "gen", "nswarm", "evals", "avg", "min" #"error", "offline_error",

        swarm = toolbox.swarm(n=NPARTICLES)

        generation = 0
        while self.iteration < 5e5:
            # Evaluate each particle in the swarm
            for part in swarm:
                part.fitness.values = toolbox.evaluate(part)
                if not part.best or part.bestfit < part.fitness:
                    part.best = toolbox.clone(part[:])  # Get the position
                    part.bestfit.values = part.fitness.values  # Get the fitness


            # Sort swarm into species, best individual comes first
            sorted_swarm = sorted(swarm, key=lambda ind: ind.bestfit, reverse=True)
            species = []
            while sorted_swarm:
                found = False
                for s in species:
                    dist = math.sqrt(sum((x1 - x2) ** 2 for x1, x2 in zip(sorted_swarm[0].best, s[0].best)))
                    if dist <= RS:
                        found = True
                        s.append(sorted_swarm[0])
                        break
                if not found:
                    species.append([sorted_swarm[0]])
                sorted_swarm.pop(0)

            record = stats.compile(swarm)
            logbook.record(gen=generation, evals=self.iteration, nswarm=len(species),
                          **record) # error=mpb.currentError(), offline_error=mpb.offlineError(),

            if self.verbose:
                print('\n\n######################################\n')
                print(logbook.stream)
                print('\n######################################\n\n')
                test_suite = pd.read_csv(self.sample_path)
                self.plotting(test_suite, self.figs_path, generation)

            # print('-------------------------------------------------local search:')
            for i, s in enumerate(species):
                for j, part in enumerate(s):
                    if len(part.fitness.values) > 0 and part.statues == 1: # and part.fitness.values[0] != 0:
                        new_part, fitness, label = local_search(toolbox.clone(part[:]),
                                                          toolbox.clone(part.fitness.values[0]), part.statues, self.delta, self.N,
                                                          self.evaluate_function)
                        fitness_min = toolbox.clone(part.fitness)
                        fitness_min.values = fitness
                        # Update swarm's attractors personal best and global best
                        if not part.best or fitness_min > part.bestfit:
                            part.best = toolbox.clone(new_part[:])
                            part.bestfit.values = fitness_min.values
                            part.statues = label
                        if not species[i].best or fitness_min > species[i].bestfit:
                            species[i].best = toolbox.clone(new_part[:])
                            species[i].bestfit.values = fitness_min.values


            # Detect change
            if any(s[0].bestfit.values != toolbox.evaluate(s[0].best) for s in species):
                # Convert particles to quantum particles
                for s in species:
                    s[:] = toolbox.convert(s, rcloud=RCLOUD, centre=s[0].best)

            else:
                # Replace exceeding particles in a species with new particles
                for s in species:
                    if len(s) > PMAX:
                        n = len(s) - PMAX
                        del s[PMAX:]
                        s.extend(toolbox.swarm(n=n))

                # Update particles that have not been reinitialized
                for s in species[:-1]:
                    for part in s[:PMAX]:
                        toolbox.update(part, s[0].best)
                        del part.fitness.values

            # Return all but the worst species' updated particles to the swarm
            # The worst species is replaced by new particles
            swarm = list(itertools.chain(toolbox.swarm(n=len(species[-1])), *species[:-1]))

            generation += 1


    # if __name__ == '__main__':
    #     main()
