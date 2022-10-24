import os
import pandas as pd
from scipy.io import arff
from .Utils import Files
from .Arguments import EnvData


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

    def load(self, name, class_name="class"):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = arff.loadarff(file_name)
        df = pd.DataFrame(data[0])
        y = df[class_name]
        X = data.drop(class_name, axis=1).to_numpy()
        y = data[class_name].to_numpy()
        return X, y


class DatasetsTanveer:
    @staticmethod
    def dataset_names(name):
        return f"{name}_R.dat"

    @staticmethod
    def folder():
        return "data"

    def load(self, name):
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

    def load(self, name):
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
        self.dataset = class_name()
        if dataset_name is None:
            file_name = os.path.join(self.dataset.folder(), Files.index)
            with open(file_name) as f:
                self.data_sets = f.read().splitlines()
        else:
            self.data_sets = [dataset_name]

    def load(self, name):
        try:
            return self.dataset.load(name)
        except FileNotFoundError:
            raise ValueError(f"Unknown dataset: {name}")

    def __iter__(self) -> Diterator:
        return Diterator(self.data_sets)
