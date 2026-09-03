import random
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy
import numpy as np
from src.GA.local_search import hill_climbing


# Pure genetic algorithm
class GA:
    def __init__(self, function, vartype, varbound, output_path, function_name,
                 algorithm_parameters={'test_budget': 100}):
        self.fitness_function = function
        self.dimension = len(vartype)
        self.vartype = vartype
        self.varbound = varbound
        self.answer_list = list()
        self.function_name = function_name

        self.min_coord = varbound[0][0]
        self.max_coord = varbound[0][1]
        self.figs_path = f'{output_path}/Domain'
        self.sample_path = f'{output_path}/Domain/{function_name}_GA_domain.csv'
        self.verbose = True
        self.output_path = output_path
        self.candidates = list()
        self.delta = 0.5
        self.N = 20

    def create_population(self, dim, min, max):
        return [random.uniform(min, max) for _ in range(dim)]

    def evaluate_population(self, population):
        fitness_list = []
        with open(self.sample_path, 'a', newline='') as file:
            for part in population:
                branch_distance, approach_level, fitness, label = self.fitness_function(part)
                fitness_list.append(fitness)
                # append to sample_file
                writer = csv.writer(file)
                writer.writerow([*part, branch_distance, approach_level, fitness, label])
        return list(zip(population, fitness_list))
        # winner = min(competition, key=lambda x: x[0])

    def selection(self, competition):
        competition.sort(key=lambda x: x[1])
        winner = competition[:10]
        # winner = min(competition, key=lambda x: x[1])
        return winner

    def crossover(self, parent1, parent2):
        pos = random.randint(1, len(parent1))
        offspring1 = parent1[:pos] + parent2[pos:]
        offspring2 = parent2[:pos] + parent1[pos:]
        return offspring1, offspring2

    def mutate(self, chromosome, min, max):
        mutated = chromosome[:]
        P = 1.0 / len(mutated)
        for pos in range(len(mutated)):
            if random.random() < P:
                mutated[pos] = random.uniform(min, max)
        return mutated

    def plotting(self, data_set, figs_path, generation):
        ds = data_set.loc[(data_set['fitness'] == 0)]
        if not ds.empty:
            print('find ................................................')
            print(ds)
        # ds = data_set
        if len(ds) == 0:
            return
        if self.dimension == 2:
            print('.............plotting: {}...........................'.format(
                ds.groupby(['x', 'y'], as_index=False).count()))
            plt.scatter(ds.iloc[:, 0].to_list(), ds.iloc[:, 1].to_list(), s=5)
            # pts = np.array([[-4.053836582, -2.827101845], [3.542466494, -3.816595838], [-2.420214529, -3.036474555],
            #                 [-0.09342022, -3.339746182]])
            # # pts = np.array([[-2.420214529, -3.036474555]])
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
        return ds

    def run_GA(self, ngen):
        # np.dtype(float)
        generation = 0

        NDIM = self.dimension
        BOUNDS = [self.min_coord, self.max_coord]
        NSWARMS = 30
        population = [self.create_population(NDIM, BOUNDS[0], BOUNDS[1]) for _ in range(NSWARMS)]
        print(population)
        eval_pop = self.evaluate_population(population)
        winners = self.selection(eval_pop)
        print("Best fitness of initial population: {a} ".format(a=winners[0]))
        counter = 0
        while generation < ngen:
            new_population = []
            while counter < len(winners):
                # Selection
                offspring1 = winners[counter][0]
                offspring2 = winners[counter + 1][0]

                counter += 2

                # Crossover
                if random.random() < 0.99:
                    (offspring1, offspring2) = self.crossover(offspring1, offspring2)
                # Mutation
                offspring1 = self.mutate(offspring1, BOUNDS[0], BOUNDS[1])
                offspring2 = self.mutate(offspring2, BOUNDS[0], BOUNDS[1])

                new_population.append(offspring1)
                new_population.append(offspring2)

            counter = 0
            generation += 1
            population = new_population
            eval_pop = self.evaluate_population(population)
            winners = self.selection(eval_pop)

            print("Best fitness  at generation {a}: {b} ".format(a=generation, b=winners[0]))
            test_suite = pd.read_csv(self.sample_path)
            ds_with_fit0 = self.plotting(test_suite, self.figs_path, generation)

            # if ds_with_fit0 is not None:
            #     for ind in ds_with_fit0.index:
            #         sample = [ds_with_fit0['x'][ind], ds_with_fit0['y'][ind]]
            #         if sample not in self.candidates:
            #             self.candidates.append(sample)
            # if len(self.candidates) > 5:
            #     return np.array(self.candidates)
