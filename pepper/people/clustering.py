from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn import metrics

import matplotlib.pyplot as plt

import numpy as np
import os


def load_data_set(directory, min_samples = 30):
    ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
    NAMES = os.path.join(ROOT, 'names.txt')
    MATRIX = os.path.join(ROOT, 'matrix.bin')

    with open(NAMES) as names_file:
        names = names_file.read().split('\n')

    matrix = np.fromfile(MATRIX, np.float32).reshape(-1, 128)

    data = {}

    for name, vector in zip(names, matrix):
        if not name in data: data[name] = []
        data[name].append(vector)

    data = {name: np.array(vectors) for name, vectors in data.items() if len(vectors) > min_samples}

    return data


def load_people():
    ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'leolani')

    data = {}

    for matrix_path in os.listdir(ROOT):
        data[os.path.splitext(matrix_path)[0]] = np.fromfile(os.path.join(ROOT, matrix_path), np.float32).reshape(-1, 128)

    return data


class PeopleCluster:
    def __init__(self, people):
        self.people = people

        # Data Organisation #
        self._names = sorted(self.people.keys())
        self._matrices = [self.people[name] for name in self._names]
        self._means = np.concatenate([np.mean(matrix, 0, keepdims=True) for matrix in self._matrices])

        self._true_labels = np.concatenate([[i] * len(self._matrices[i]) for i in range(len(self._names))])

        # Clustering #
        self._data = np.concatenate(self._matrices)
        self._cluster = KMeans(len(people), init=self._means, n_init=1)
        self._labels = self._cluster.fit_predict(self._data)
        self._centers = self._cluster.cluster_centers_

    def classify(self, face):
        distances = np.linalg.norm(self._means - face, 2, 1)
        labels = np.argsort(distances)
        index = labels[0]

        # Silhouette Score
        a = np.mean(np.linalg.norm(self._data[np.where(self._labels == labels[0])] - face, 2, 1))
        b = np.mean(np.linalg.norm(self._data[np.where(self._labels == labels[1])] - face, 2, 1))
        s = (b - a) / max(a, b)

        name = self._names[index]
        distance = distances[index]

        return name, s

    def performance(self):
        print("Accuracy: {}".format(metrics.accuracy_score(self._true_labels, self._labels)))
        print("Precision: {}".format(metrics.precision_score(self._true_labels, self._labels, average='macro')))
        print("Recall: {}".format(metrics.recall_score(self._true_labels, self._labels, average='macro')))
        print("Silhouette Score: {}".format(metrics.silhouette_score(self._data, self._labels)))

    def plot(self):
        pca = PCA(2)
        pca.fit(self._data)
        data_pca = pca.transform(self._data)

        for index in range(len(people)):
            cluster_data = data_pca[np.where(self._labels == index)]
            plt.scatter(cluster_data[:, 0], cluster_data[:, 1], cmap='tab20', label=self._names[index])

        plt.legend()
        plt.show()


if __name__ == "__main__":
    people = load_data_set('lfw', 100)
    people.update(load_people())

    cluster = PeopleCluster(people)
    cluster.performance()
    cluster.plot()
