import numpy as np
import cvxpy as cvx
import matplotlib.pyplot as plt
import tqdm
import copy
import sklearn.datasets
from matplotlib import pyplot
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV


class SupportVectorClustering:
    
    def __init__(self):
        self.support_vectors = None
        self.boundry_support_vectors = None
        self.svs = None
        self.xs = None
        self.q = None
        self.C = None
        self.km = None
        self.beta = None
        self.svs = None
        self.bsvs = None
        self.adj = None

    def dataset(self,xs):
        self.xs = xs

    def parameters(self, C=0.1, q=1):
        self.q = q
        self.C = C

    def kernel(self, x1, x2):
        return np.exp(-self.q * np.sum((x1 - x2)**2, axis=-1))

    def kernel_matrix(self, x1, x2):
        km = np.zeros((x1.shape[0], x2.shape[0]))
        for i in range(x1.shape[0]):
            for j in range(x2.shape[0]):
                km[i, j] = self.kernel(x1[i], x2[j])

        return km

    def r_func(self, x, xs, beta, km):
        return 1 - 2*np.sum([beta[i] * self.kernel(xs[i], x) for i in range(len(xs))]) + beta.T @ km @ beta

    def find_beta(self, km):
        beta = cvx.Variable(len(km))
        objective = cvx.Maximize(cvx.sum(beta) - cvx.quad_form(beta, km))
        constraints = [0<=beta, beta<=self.C, cvx.sum(beta)==1]
        prob = cvx.Problem(objective, constraints)
        _ = prob.solve()
        
        return beta.value

    def sample_segment(self, x1, x2, r, xs, beta, km, n=10):
        for i in range(n):
            # a point on the line connecting x1 to x2
            x = x1 + (x2 - x1) * i / (n + 1)
            if self.r_func(x, xs, beta, km) > r:
                return False

        return True

    def cluster(self, xs):
        N = len(xs)

        self.km = self.kernel_matrix(xs, xs)
        self.beta = self.find_beta(self.km)

        svs = np.where(np.logical_and(1e-8 < self.beta, self.beta < self.C))[0]
        bsvs = np.where(self.beta >= self.C)[0]

        r = np.max([self.r_func(xs[i], xs, self.beta, self.km) for i in svs])

        adj = np.zeros((N, N))
        for i in tqdm.tqdm(range(N)):
            if i not in bsvs:
                for j in range(i, N):
                    if j not in bsvs:
                        adj[i, j] = adj[j, i] = self.sample_segment(xs[i], xs[j], r, xs, self.beta, self.km)

        return svs, bsvs, adj

    def cluster_incremental(self, chunk_size):
        for i in range(len(self.xs) // chunk_size):
            print("Fitting step", i)

            xs = self.xs[i*chunk_size:(i+1)*chunk_size]

            if self.support_vectors is not None:
                xs = np.concatenate([xs, self.support_vectors])

            if self.boundry_support_vectors is not None and self.boundry_support_vectors.shape[0] != 0:
                xs = np.concatenate([xs, self.boundry_support_vectors])

            self.current_chunk = xs
            svs, bsvs, adj = self.cluster(xs)
            self.svs, self.bsvs, self.adj = svs, bsvs, adj

            self.support_vectors = np.array(list(map(lambda i: xs[i], svs)))
            self.boundry_support_vectors = np.array(list(map(lambda i: xs[i], bsvs)))

    def return_sv_clusters(self):
        num_clusters = -1
        sv_clusters = {}
        ids = list(self.svs)
        while ids:
            num_clusters += 1
            sv_clusters[num_clusters] = []
            curr_id = ids.pop(0)
            queue = [curr_id]
            while queue:
                cid = queue.pop(0)
                for i in ids:
                    if self.adj[i, cid]:
                        queue.append(i)
                        ids.remove(i)

                sv_clusters[num_clusters].append(cid)

        return sv_clusters

def isvc(ms):
    ssvc = SupportVectorClustering()
    ssvc.dataset(ms)
    ssvc.parameters(C=0.1, q=7)

    ssvc.cluster_incremental(10)

    sv_clusters = ssvc.return_sv_clusters()
    print(sv_clusters)

    # Plot support vectors
    if len(sv_clusters[0]) > 0:
        sv_0 = np.array(list(map(lambda i: ssvc.current_chunk[i], sv_clusters[0])))
    if len(sv_clusters[1]) > 0:
        sv_1 = np.array(list(map(lambda i: ssvc.current_chunk[i], sv_clusters[1])))

    if len(sv_clusters[0]) == 0 or len(sv_clusters[1]) == 0:
        return

    return sv_0, sv_1

    plt.scatter(ms[:, 0], ms[:, 1], c="b")
    # plt.scatter(ssvc.support_vectors[:, 0], ssvc.support_vectors[:, 1], c="r")
    plt.scatter(sv_0[:, 0], sv_0[:, 1], c="k")
    plt.scatter(sv_1[:, 0], sv_1[:, 1], c="y")

    plt.show()

    # Train SVM on support vectors' classes
    sv_dataset = np.concatenate([sv_0, sv_1])
    sv_labels = np.concatenate([np.zeros((sv_0.shape[0], 1)), np.ones((sv_1.shape[0], 1))])
    dataset = np.hstack([sv_dataset, sv_labels])
    np.random.shuffle(dataset)

    X = dataset[:, 0:2]
    y = dataset[:, 2]

    parameters = {
        'C': [0.001, 0.01, 0.1, 1, 10],
        'gamma': ["auto", "scale", 0.001, 0.01, 1],
        'kernel': ["linear", "poly", "rbf", "sigmoid"],
    }
    grid = GridSearchCV(estimator=SVC(), param_grid=parameters)
    grid.fit(X, y)

    print(grid.best_score_)

    clf = grid.best_estimator_

    # Predict class of other samples using trained SVM model
    predictions = clf.predict(ms)
    cluster_0 = ms[predictions == 0]
    cluster_1 = ms[predictions == 1]

    pyplot.scatter(ms[:, 0], ms[:, 1], c="b")
    pyplot.scatter(cluster_0[:, 0], cluster_0[:, 1], c="k")
    pyplot.scatter(cluster_1[:, 0], cluster_1[:, 1], c="y")

    pyplot.show()


if __name__ == "__main__":
    ms = sklearn.datasets.make_moons(n_samples=500, noise=0.08, random_state=4)[0]
    isvc(ms)