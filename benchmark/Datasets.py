import os
from types import SimpleNamespace
import pandas as pd
import numpy as np
import json
from scipy.io import arff
from .Utils import Files
from .Arguments import EnvData
from fimdlp.mdlp import FImdlp


class Diterator:
    def __init__(self, data):
        self._stack = data.copy()

    def __next__(self):
        if len(self._stack) == 0:
            raise StopIteration()
        return self._stack.pop(0)


class DatasetsArff:
    @staticmethod
    def dataset_names(name):
        return f"{name}.arff"

    @staticmethod
    def folder():
        return "datasets"

    @staticmethod
    def get_range_features(X, c_features):
        if c_features.strip() == "all":
            return list(range(X.shape[1]))
        return json.loads(c_features)

    def load(self, name, class_name):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = arff.loadarff(file_name)
        df = pd.DataFrame(data[0])
        df.dropna(axis=0, how="any", inplace=True)
        self.dataset = df
        X = df.drop(class_name, axis=1)
        self.features = X.columns.to_list()
        self.class_name = class_name
        y, _ = pd.factorize(df[class_name])
        X = X.to_numpy()
        return X, y


class DatasetsTanveer:
    @staticmethod
    def dataset_names(name):
        return f"{name}_R.dat"

    @staticmethod
    def folder():
        return "data"

    @staticmethod
    def get_range_features(X, name):
        return []

    def load(self, name, *args):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = pd.read_csv(
            file_name,
            sep="\t",
            index_col=0,
        )
        X = data.drop("clase", axis=1)
        self.features = X.columns
        X = X.to_numpy()
        y = data["clase"].to_numpy()
        self.dataset = data
        self.class_name = "clase"
        return X, y


class DatasetsSurcov:
    @staticmethod
    def dataset_names(name):
        return f"{name}.csv"

    @staticmethod
    def folder():
        return "datasets"

    @staticmethod
    def get_range_features(X, name):
        return []

    def load(self, name, *args):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = pd.read_csv(
            file_name,
            index_col=0,
        )
        data.dropna(axis=0, how="any", inplace=True)
        self.columns = data.columns
        X = data.drop(["class"], axis=1)
        self.features = X.columns
        self.class_name = "class"
        self.dataset = data
        X = X.to_numpy()
        y = data["class"].to_numpy()
        return X, y


class Datasets:
    def __init__(self, dataset_name=None, discretize=None):
        envData = EnvData.load()
        # DatasetsSurcov, DatasetsTanveer, DatasetsArff,...
        source_name = getattr(
            __import__(__name__),
            f"Datasets{envData['source_data']}",
        )
        self.discretize = (
            envData["discretize"] == "1"
            if discretize is None
            else discretize == "1"
        )
        self.dataset = source_name()
        # initialize self.class_names & self.data_sets
        class_names, sets = self._init_names(dataset_name)
        self.class_names = class_names
        self.data_sets = sets
        self.states = {}  # states of discretized variables

    def _init_names(self, dataset_name):
        file_name = os.path.join(self.dataset.folder(), Files.index)
        default_class = "class"
        self.continuous_features = {}
        with open(file_name) as f:
            sets = f.read().splitlines()
            class_names = [default_class] * len(sets)
        if "," in sets[0]:
            result = []
            class_names = []
            for data in sets:
                name, class_name, features = data.split(",", 2)
                result.append(name)
                class_names.append(class_name)
                self.continuous_features[name] = features
            sets = result
        else:
            for name in sets:
                self.continuous_features[name] = None
        # Set as dataset list the dataset passed as argument
        if dataset_name is None:
            return class_names, sets
        try:
            class_name = class_names[sets.index(dataset_name)]
        except ValueError:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        return [class_name], [dataset_name]

    def get_attributes(self, name):
        tmp = self.discretize
        self.discretize = False
        X, y = self.load(name)
        attr = SimpleNamespace()
        attr.dataset = name
        values, counts = np.unique(y, return_counts=True)
        comp = ""
        sep = ""
        for count in counts:
            comp += f"{sep}{count/sum(counts)*100:5.2f}%"
            sep = "/ "
        attr.balance = comp
        attr.classes = len(np.unique(y))
        attr.samples = X.shape[0]
        attr.features = X.shape[1]
        attr.cont_features = len(self.get_continuous_features())
        self.discretize = tmp
        return attr

    def get_features(self):
        return self.dataset.features

    def get_states(self, name):
        return self.states[name] if name in self.states else None

    def get_continuous_features(self):
        return self.continuous_features_dataset

    def get_class_name(self):
        return self.dataset.class_name

    def get_dataset(self):
        return self.dataset.dataset

    def build_states(self, name, X):
        features = self.get_features()
        self.states[name] = {
            features[i]: np.unique(X[:, i]).tolist() for i in range(X.shape[1])
        }

    def load(self, name, dataframe=False):
        try:
            class_name = self.class_names[self.data_sets.index(name)]
            X, y = self.dataset.load(name, class_name)
            self.continuous_features_dataset = self.dataset.get_range_features(
                X, self.continuous_features[name]
            )
            if self.discretize:
                X = self.discretize_dataset(X, y)
                self.build_states(name, X)
                dataset = pd.DataFrame(X, columns=self.get_features())
                dataset[self.get_class_name()] = y
                self.dataset.dataset = dataset
            if dataframe:
                return self.get_dataset()
            return X, y
        except (ValueError, FileNotFoundError):
            raise ValueError(f"Unknown dataset: {name}")

    def discretize_dataset(self, X, y):
        """Supervised discretization with Fayyad and Irani's MDLP algorithm.

        Parameters
        ----------
        X : np.ndarray
            array (n_samples, n_features) of features
        y : np.ndarray
            array (n_samples,) of labels

        Returns
        -------
        tuple (X, y) of numpy.ndarray
        """
        discretiz = FImdlp(algorithm=0)
        return discretiz.fit_transform(X, y)

    def __iter__(self) -> Diterator:
        return Diterator(self.data_sets)
