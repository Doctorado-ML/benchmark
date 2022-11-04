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

    def load(self, name, class_name, dataframe):
        file_name = os.path.join(self.folder(), self.dataset_names(name))
        data = arff.loadarff(file_name)
        df = pd.DataFrame(data[0])
        df = df.dropna()
        X = df.drop(class_name, axis=1)
        self.features = X.columns
        self.class_name = class_name
        y, _ = pd.factorize(df[class_name])
        return df if dataframe else (X.to_numpy(), y)


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
        self.dataset = class_name()
        self.class_names = []
        self.load_names()
        if dataset_name is not None:
            try:
                class_name = self.class_names[
                    self.data_sets.index(dataset_name)
                ]
                self.class_names = [class_name]
            except ValueError:
                raise ValueError(f"Unknown dataset: {dataset_name}")
            self.data_sets = [dataset_name]

    def load_names(self):
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

    def load(self, name, dataframe=False):
        try:
            class_name = self.class_names[self.data_sets.index(name)]
            return self.dataset.load(name, class_name, dataframe)
        except (ValueError, FileNotFoundError):
            raise ValueError(f"Unknown dataset: {name}")

    def __iter__(self) -> Diterator:
        return Diterator(self.data_sets)
