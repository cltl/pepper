from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score

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


def load_people(directory = 'leolani'):
    ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)

    data = {}
    if os.path.isdir(ROOT):
        for matrix_path in os.listdir(ROOT):
            data[os.path.splitext(matrix_path)[0]] = np.fromfile(
                os.path.join(ROOT, matrix_path), np.float32).reshape(-1, 128)

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
        inner = np.mean(np.linalg.norm(self._data[np.where(self._labels == labels[0])] - face, 2, 1))
        outer = np.mean(np.linalg.norm(self._data[np.where(self._labels == labels[1])] - face, 2, 1))
        silhouette = (outer - inner) / max(inner, outer)

        name = self._names[index]

        return name, silhouette

    def performance(self):
        print("Accuracy: {}".format(metrics.accuracy_score(self._true_labels, self._labels)))
        print("Precision: {}".format(metrics.precision_score(self._true_labels, self._labels, average='macro')))
        print("Recall: {}".format(metrics.recall_score(self._true_labels, self._labels, average='macro')))
        print("Silhouette Score: {}".format(metrics.silhouette_score(self._data, self._labels)))

    def plot(self):
        pca = PCA(2)
        data_pca = pca.fit_transform(self._data)

        for index in range(len(self.people)):
            cluster_data = data_pca[np.where(self._labels == index)]
            plt.scatter(cluster_data[:, 0], cluster_data[:, 1], cmap='tab20', label=self._names[index])

        plt.legend()
        plt.show()


class PeopleClassifier:

    LEOLANI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'leolani')

    FEATURE_DIM = 128

    def __init__(self, people, n_neighbors=20):
        self._people = people
        self._names = sorted(people.keys())
        self._indices = range(len(self._names))

        self._labels = np.concatenate([[index] * len(people[name]) for name, index in zip(self._names, self._indices)])
        self._features = np.concatenate([people[name] for name in self._names])

        self._classifier = KNeighborsClassifier(n_neighbors)
        self._classifier.fit(self._features, self._labels)

    @property
    def people(self):
        return self._people

    def classify(self, face):
        distances, indices = self._classifier.kneighbors(face.reshape(-1, self.FEATURE_DIM))
        distances, indices = distances[0], indices[0]

        labels = self._labels[indices]
        label = np.bincount(labels).argmax()
        name = self._names[label]
        confidence = np.mean(labels == label)
        distance = np.mean(distances[labels == label])
        return name, confidence, distance

    def accuracy(self):
        return np.mean(cross_val_score(self._classifier, self._features, self._labels, cv=5))

    @classmethod
    def from_directory(cls, directory):
        return cls(PeopleClassifier.load_directory(directory))

    @staticmethod
    def load_directory(directory):
        people = {}
        for path in os.listdir(directory):
            name = os.path.splitext(path)[0]
            features = np.fromfile(os.path.join(directory, path), np.float32).reshape(-1, PeopleClassifier.FEATURE_DIM)
            people[name] = features
        return people


if __name__ == "__main__":
    pass