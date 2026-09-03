import random
import csv
import matplotlib.pyplot as plt
import pandas as pd
from src.GA.local_search import hill_climbing
import datetime
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_validate
import time
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score as si
import concurrent.futures


# Genetic with local search
class GA_Local:
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
        self.sample_path = f'{output_path}/Domain/{function_name}_GA_Local_domain.csv'
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

    def selection(self, competition):
        competition.sort(key=lambda x: x[1])
        winner = competition[:20]
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
            # pts = np.array([[5, 10], [16, 15], [17, 20], [27, 20], [45, 25]])
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

    def cal_silhouette_score(self, test_suite):
        print("clustering model")
        ds_with_label1 = test_suite.loc[(test_suite['label'] == 1)].loc[:, ["x", "y"]]
        arr = ds_with_label1.to_numpy()
        clusters = DBSCAN()
        clusters.fit(arr)
        labels = list(clusters.labels_)
        silhouette_score = si(arr, labels, metric='euclidean')
        print('silhouette_score: %.3f' % silhouette_score)
        return silhouette_score

    def terminate_GA(self, test_suite):
        print("classification model")
        test_suite = test_suite.loc[:, ["x", "y", "label"]]
        # test_suite = test_suite.loc[:, ["f", "d", "a", "h", "label"]]
        # test_suite = test_suite.loc[:, ["d", "f", "a", "i", "label"]]
        # test_suite = test_suite.loc[:, ["e", "a", "label"]]
        # test_suite = test_suite.loc[:, ["h", "i", "label"]]
        # test_suite = test_suite.loc[:, ["d", "f", "i", "label"]]
        # test_suite = test_suite.loc[:, ["f", "d", "h", "label"]]
        ds_with_label1 = test_suite.loc[(test_suite['label'] == 1)]
        ds_with_label0 = test_suite.loc[(test_suite['label'] == 0)]
        ds_with_label0_new = ds_with_label0.sample(n=min(ds_with_label1.shape[0], ds_with_label0.shape[0]))
        final_df = pd.concat([ds_with_label0_new, ds_with_label1], axis=0)
        Y_col = 'label'
        X_cols = final_df.loc[:, final_df.columns != Y_col].columns
        # prepare the cross-validation procedure
        cv = KFold(n_splits=10, random_state=1, shuffle=True)
        # create model
        max_depth = final_df.shape[0] * 0.1
        clf = RandomForestClassifier(max_depth=max_depth, random_state=0, n_jobs=-1)
        print("model is created ...")
        # evaluate model
        scoring = ['accuracy', 'f1']
        scores = cross_validate(clf, final_df[X_cols], final_df[Y_col], cv=cv,
                                scoring=scoring, return_train_score=False)
        print(scores.keys())
        print(scores.values())
        print(scores['test_accuracy'].mean())
        print(scores['test_f1'].mean())
        accuracy = scores['test_accuracy'].mean()
        f1 = scores['test_f1'].mean()

        # f1 = cross_val_score(svc, final_df[X_cols], final_df[Y_col], scoring='f1', cv=cv, n_jobs=-1).mean()
        # print('Accuracy: %.3f' % accuracy)
        # print('F1 Score: %.3f' % f1)
        return accuracy, f1

    def run_GA_local(self, ngen):
        # get the start time
        st = time.time()

        accuracy_per_generation = []
        f1_per_generation = []
        silhouette_score_per_generation = []

        # np.dtype(float)
        generation = 0
        local_search_rate = 5
        local_search_budget = 20

        NDIM = self.dimension
        BOUNDS = [self.min_coord, self.max_coord]
        popSize = 100
        population = [self.create_population(NDIM, BOUNDS[0], BOUNDS[1]) for _ in range(popSize)]
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
                if random.random() < 0.9:
                    (offspring1, offspring2) = self.crossover(offspring1, offspring2)
                # Mutation
                offspring1 = self.mutate(offspring1, BOUNDS[0], BOUNDS[1])
                offspring2 = self.mutate(offspring2, BOUNDS[0], BOUNDS[1])

                new_population.append(offspring1)
                new_population.append(offspring2)

                # # approach2:
                # if random.random() < 0.1:
                #     print('-------------------------------------------------local search:')
                #     for i, part in enumerate(population):
                #         branch_distance, approach_level, fitness, label = self.fitness_function(part)
                #         new_part, new_fitness = hill_climbing(part, fitness, self.delta, self.N, self.evaluate_function)
                #         new_population.append(new_part)
                # if local_search_rate == 0:
                #     local_search_rate = 10

                if generation % local_search_rate == 0:
                    print('-------------------------------------------------local search:')
                    for i in range(local_search_budget):
                        branch_distance, approach_level, fitness, label = self.fitness_function(population[i])
                        new_part, new_fitness = hill_climbing(population[i], fitness, self.delta, self.N,
                                                              self.evaluate_function)
                        new_population.append(new_part)
                # else:
                #     pass

            counter = 0
            generation += 1
            population = new_population
            eval_pop = self.evaluate_population(population)
            winners = self.selection(eval_pop)

            print("Best fitness  at generation {a}: {b} ".format(a=generation, b=winners[0]))
            test_suite = pd.read_csv(self.sample_path)
            ds_with_fit0 = self.plotting(test_suite, self.figs_path, generation)
            if (generation % 100 == 0) and (ds_with_fit0 is not None):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future1 = executor.submit(self.terminate_GA, test_suite)
                    # future2 = executor.submit(self.cal_silhouette_score, test_suite)
                    return_value1, return_value2 = future1.result()
                    # return_value3 = future2.result()
                    # print(return_value1)
                    # print(return_value2)
                    accuracy_per_generation.append(return_value1)
                    f1_per_generation.append(return_value2)
                    # silhouette_score_per_generation.append(return_value3)
                    # time.sleep(10)
            if len(f1_per_generation) > 3 and abs(f1_per_generation[-1] - f1_per_generation[-2]) < 0.01:
                break

        # get the end time
        et = time.time()

        # get the execution time
        elapsed_time = et - st
        print('Execution time:', elapsed_time, 'seconds')
        print("acc = ", accuracy_per_generation)
        # print("sil = ", silhouette_score_per_generation)
        print("f1 = ", f1_per_generation)
