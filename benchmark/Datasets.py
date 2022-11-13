import os
import pandas as pd
import numpy as np
from scipy.io import arff
from .Utils import Files
from .Arguments import EnvData
from mdlp.discretization import MDLP


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

    def load(self, name, class_name, dataframe):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = arff.loadarff(file_name)
        df = pd.DataFrame(data[0])
        df.dropna(axis=0, how="any", inplace=True)
        X = df.drop(class_name, axis=1)
        self.features = X.columns
        self.class_name = class_name
        y, _ = pd.factorize(df[class_name])
        df[class_name] = y
        X = X.to_numpy()
        return df if dataframe else (X, y)


class DatasetsTanveer:
    @staticmethod
    def dataset_names(name):
        return f"{name}_R.dat"

    @staticmethod
    def folder():
        return "data"

    def load(self, name, *args):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = pd.read_csv(
            file_name,
            sep="\t",
            index_col=0,
        )
        X = data.drop("clase", axis=1).to_numpy()
        y = data["clase"].to_numpy()
        return X, y


class DatasetsSurcov:
    @staticmethod
    def dataset_names(name):
        return f"{name}.csv"

    @staticmethod
    def folder():
        return "datasets"

    def load(self, name, *args):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = pd.read_csv(
            file_name,
            index_col=0,
        )
        data.dropna(axis=0, how="any", inplace=True)
        self.columns = data.columns
        col_list = ["class"]
        X = data.drop(col_list, axis=1).to_numpy()
        y = data["class"].to_numpy()
        return X, y


class Datasets:
    def __init__(self, dataset_name=None):
        envData = EnvData.load()
        class_name = getattr(
            __import__(__name__),
            f"Datasets{envData['source_data']}",
        )
        self.load = (
            self.load_discretized
            if envData["discretize"] == "1"
            else self.load_continuous
        )
        self.dataset = class_name()
        self.class_names = []
        self._load_names()
        if dataset_name is not None:
            try:
                class_name = self.class_names[
                    self.data_sets.index(dataset_name)
                ]
                self.class_names = [class_name]
            except ValueError:
                raise ValueError(f"Unknown dataset: {dataset_name}")
            self.data_sets = [dataset_name]

    def _load_names(self):
        file_name = os.path.join(self.dataset.folder(), Files.index)
        default_class = "class"
        with open(file_name) as f:
            self.data_sets = f.read().splitlines()
            self.class_names = [default_class] * len(self.data_sets)
        if "," in self.data_sets[0]:
            result = []
            class_names = []
            for data in self.data_sets:
                name, class_name = data.split(",")
                result.append(name)
                class_names.append(class_name)
            self.data_sets = result
            self.class_names = class_names

    def get_attributes(self, name):
        class Attributes:
            pass

        X, y = self.load_continuous(name)
        attr = Attributes()
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
        return attr

    def get_features(self):
        return self.dataset.features

    def get_class_name(self):
        return self.dataset.class_name

    def load_continuous(self, name, dataframe=False):
        try:
            class_name = self.class_names[self.data_sets.index(name)]
            return self.dataset.load(name, class_name, dataframe)
        except (ValueError, FileNotFoundError):
            raise ValueError(f"Unknown dataset: {name}")

    def discretize(self, X, y):
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
        discretiz = MDLP()
        Xdisc = discretiz.fit_transform(X, y)
        return Xdisc.astype(int), y.astype(int)

    def load_discretized(self, name, dataframe=False):
        X, y = self.load_continuous(name)
        X, y = self.discretize(X, y)
        dataset = pd.DataFrame(X, columns=self.get_features())
        dataset[self.get_class_name()] = y
        return dataset if dataframe else X, y

    def __iter__(self) -> Diterator:
        return Diterator(self.data_sets)
